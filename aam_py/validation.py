from typing import Dict, List, TYPE_CHECKING
from aam_py.error import AamlError, SchemaValidationError, InvalidValueError, NotFoundError
from aam_py.types import resolve_builtin
from aam_py.types.list import ListType
from aam_py.parsing import is_inline_object, parse_inline_object

if TYPE_CHECKING:
    from aam_py.aaml import AAML


def validate_against_schemas(aaml: 'AAML', field: str, value: str) -> None:
    for schema_name, schema_def in aaml.get_schemas().items():
        if field in schema_def.fields:
            validate_typed_field(aaml, schema_def.fields[field], value, schema_name, field)


def validate_typed_field(aaml: 'AAML', type_name: str, value: str, schema_name: str, field: str) -> None:
    def make_err(details: str) -> SchemaValidationError:
        return SchemaValidationError(schema_name, field, type_name, details)

    type_def = aaml.get_type(type_name)
    if type_def is not None:
        try:
            type_def.validate(value)
            return
        except AamlError as e:
            raise make_err(str(e))

    nested_schema = aaml.get_schema(type_name)
    if nested_schema is not None:
        try:
            validate_inline_object_against_schema(aaml, value, type_name, nested_schema.fields)
            return
        except AamlError as e:
            raise make_err(str(e))

    inner_type = ListType.parse_inner(type_name)
    if inner_type is not None:
        try:
            validate_list_value(aaml, value, inner_type)
            return
        except AamlError as e:
            raise make_err(str(e))

    try:
        builtin = resolve_builtin(type_name)
        builtin.validate(value)
    except AamlError as e:
        if isinstance(e, NotFoundError):
            raise make_err(f"Unknown type '{type_name}'")
        raise make_err(str(e))


def validate_list_value(aaml: 'AAML', value: str, inner_type: str) -> None:
    items = ListType.parse_items(value)
    if items is None:
        raise InvalidValueError(f"Expected a list literal '[...]', got '{value}'")

    for item in items:
        nested_schema = aaml.get_schema(inner_type)
        if nested_schema is not None:
            validate_inline_object_against_schema(aaml, item, inner_type, nested_schema.fields)
            continue
            
        try:
            builtin = resolve_builtin(inner_type)
            builtin.validate(item)
            continue
        except AamlError as e:
            if not isinstance(e, NotFoundError):
                raise InvalidValueError(f"List item '{item}' failed for type '{inner_type}': {e}")
                
        type_def = aaml.get_type(inner_type)
        if type_def is not None:
            try:
                type_def.validate(item)
                continue
            except AamlError as e:
                raise InvalidValueError(f"List item '{item}' failed for type '{inner_type}': {e}")
                
        raise NotFoundError(f"Unknown list element type '{inner_type}'")


def validate_inline_object_against_schema(
    aaml: 'AAML', value: str, schema_name: str, schema_fields: Dict[str, str]
) -> None:
    if not is_inline_object(value):
        raise InvalidValueError(
            f"Field typed as schema '{schema_name}' must be an inline object '{{ k = v, ... }}', got: '{value}'"
        )
        
    try:
        pairs = parse_inline_object(value)
    except Exception as e:
        raise InvalidValueError(f"Failed to parse inline object for schema '{schema_name}': {e}")
        
    pair_map = dict(pairs)
    
    schema_def = aaml.get_schema(schema_name)
    optional_fields = schema_def.optional_fields if schema_def else set()

    for field, type_name in schema_fields.items():
        if field not in pair_map:
            if field not in optional_fields:
                raise SchemaValidationError(
                    schema_name, field, type_name,
                    f"Missing field '{field}' in inline object for schema '{schema_name}'"
                )
        else:
            validate_typed_field(aaml, type_name, pair_map[field], schema_name, field)


def validate_schemas_completeness(aaml: 'AAML') -> None:
    names = list(aaml.get_schemas().keys())
    validate_schemas_completeness_for(aaml, names)


def validate_schemas_completeness_for(aaml: 'AAML', schema_names: List[str]) -> None:
    aaml_map = aaml.get_map()
    for name in schema_names:
        schema_def = aaml.get_schema(name)
        if schema_def is None:
            continue
            
        for field, type_name in schema_def.fields.items():
            if schema_def.is_optional(field):
                continue
            if field not in aaml_map:
                raise SchemaValidationError(
                    name, field, type_name,
                    f"Missing required field '{field}'"
                )

def apply_schema(aaml: 'AAML', schema_name: str, data: Dict[str, str]) -> None:
    schema_def = aaml.get_schema(schema_name)
    if schema_def is None:
        raise NotFoundError(f"Schema '{schema_name}' not found")

    optional = schema_def.optional_fields
    for field, type_name in schema_def.fields.items():
        if field not in data:
            if field not in optional:
                raise SchemaValidationError(
                    schema_name, field, type_name,
                    f"Missing required field '{field}'"
                )
        else:
            validate_typed_field(aaml, type_name, data[field], schema_name, field)
