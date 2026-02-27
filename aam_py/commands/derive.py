from aam_py.error import ParseError
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aam_py.aaml import AAML

class DeriveCommand:
    @property
    def name(self) -> str:
        return "derive"

    def execute(self, aaml: 'AAML', args: str) -> None:
        parts = [p.strip() for p in args.split('::')]
        if not parts or not parts[0]:
            raise ParseError(0, f"@derive {args}", "Missing file path")
            
        file_path = aaml.unwrap_quotes(parts[0])
        schema_names = parts[1:]
        
        # We need a new AAML instance to parse the base file
        from aam_py.aaml import AAML
        try:
            base_config = AAML.load(file_path)
        except Exception as e:
            raise ParseError(0, f"@derive {args}", f"Failed to load derived file: {e}")
            
        if schema_names:
            # We ONLY copy the keys defined by the specified schemas
            for name in schema_names:
                schema_def = base_config.get_schema(name)
                if not schema_def:
                    raise ParseError(0, f"@derive {args}", f"Schema '{name}' not found in '{file_path}'")
                    
                aaml._schemas[name] = schema_def
                
                for field in schema_def.fields:
                    val = base_config.get_map().get(field)
                    if val is not None:
                        aaml.get_map().setdefault(field, val)
        else:
            # Inherit everything but do not overwrite existing keys
            for k, v in base_config.get_map().items():
                aaml.get_map().setdefault(k, v)
                
            # Copy schemas and types as well
            for k, v in base_config._schemas.items():
                if k not in aaml._schemas:
                    aaml._schemas[k] = v
            for k, v in base_config._types.items():
                if k not in aaml._types:
                    aaml._types[k] = v
                    
        # Validate completeness
        if schema_names:
            from aam_py.validation import validate_schemas_completeness_for
            validate_schemas_completeness_for(base_config, schema_names)
                
        from aam_py.validation import validate_schemas_completeness
        validate_schemas_completeness(aaml)
