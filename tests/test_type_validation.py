import pytest
from aam_py import AAML, SchemaValidationError, InvalidTypeError

def test_builtin_types():
    aaml = AAML()
    
    aaml.validate_value("i32", "123")
    
    with pytest.raises(InvalidTypeError):
        aaml.validate_value("i32", "abc")
        
    aaml.validate_value("bool", "true")
    
    with pytest.raises(InvalidTypeError):
        aaml.validate_value("bool", "yes")
        
    aaml.validate_value("f64", "3.14")

def test_schema_field_validation():
    config = """
    @schema Device {
        id: i32,
        name: string
    }

    id = 42
    name = "Sensor A"
    """
    
    aaml = AAML.parse(config)
    from aam_py.validation import validate_schemas_completeness
    validate_schemas_completeness(aaml)

def test_schema_validation_failure():
    config = """
    @schema Device {
        id: i32
    }

    id = "not_a_number"
    """
    with pytest.raises(SchemaValidationError):
        AAML.parse(config)

def test_apply_schema_manual():
    aaml = AAML()
    aaml.merge_content("@schema Point { x: i32, y: i32 }")
    
    data = {"x": "10", "y": "20"}
    from aam_py.validation import apply_schema
    apply_schema(aaml, "Point", data)
    
    data["y"] = "invalid"
    with pytest.raises(SchemaValidationError):
        apply_schema(aaml, "Point", data)
