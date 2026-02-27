import pytest
from aam_py import AAML, AAMBuilder, SchemaField, SchemaValidationError, ParseError, InvalidTypeError

def test_derive_inherits_keys(tmp_path):
    base_file = tmp_path / "test_derive_base_inherit.aam"
    base = AAMBuilder()
    base.add_line("base_key", "base_val")
    base.add_line("shared_key", "from_base")
    base.to_file(base_file)

    content = f"@derive {base_file}\nchild_key = child_val\n"
    parser = AAML.parse(content)

    assert parser.find_obj("base_key") == "base_val"
    assert parser.find_obj("child_key") == "child_val"

def test_derive_does_not_overwrite_child_keys(tmp_path):
    base_file = tmp_path / "test_derive_no_overwrite.aam"
    base = AAMBuilder()
    base.add_line("shared_key", "from_base")
    base.to_file(base_file)

    content = f"shared_key = from_child\n@derive {base_file}\n"
    parser = AAML.parse(content)

    assert parser.find_obj("shared_key") == "from_child"

def test_derive_with_quoted_path(tmp_path):
    base_file = tmp_path / "test_derive_quoted.aam"
    base = AAMBuilder()
    base.add_line("q_key", "q_val")
    base.to_file(base_file)

    content = f'@derive "{base_file}"'
    parser = AAML.parse(content)

    assert parser.find_obj("q_key") == "q_val"

def test_derive_inherits_schemas(tmp_path):
    base_file = tmp_path / "test_derive_schemas.aam"
    base = AAMBuilder()
    base.schema("Point", [SchemaField.required("x", "f64"), SchemaField.required("y", "f64")])
    base.add_line("x", "1.0")
    base.add_line("y", "2.0")
    base.add_line("origin", "0.0, 0.0")
    base.to_file(base_file)

    content = f"@derive {base_file}\n"
    parser = AAML.parse(content)

    assert parser.get_schema("Point") is not None
    assert parser.find_obj("origin") == "0.0, 0.0"
    assert parser.find_obj("x") == "1.0"
    assert parser.find_obj("y") == "2.0"

def test_derive_schema_not_overwritten_by_base(tmp_path):
    base_file = tmp_path / "test_derive_schema_nowipe.aam"
    base = AAMBuilder()
    base.schema("Config", [SchemaField.required("timeout", "i32")])
    base.add_line("timeout", "30")
    base.to_file(base_file)

    content = f"@schema Config {{ timeout: f64, retries: i32 }}\ntimeout = 5.0\nretries = 3\n@derive {base_file}\n"
    parser = AAML.parse(content)

    schema = parser.get_schema("Config")
    assert schema is not None
    assert "retries" in schema.fields
    assert schema.fields["timeout"] == "f64"

def test_derive_missing_file_error():
    content = "@derive non_existent_file_xyz.aam\n"
    with pytest.raises(ParseError):
        AAML.parse(content)

def test_derive_empty_path_error():
    content = "@derive \n"
    with pytest.raises(ParseError):
        AAML.parse(content)

def test_schema_registers_fields():
    content = "@schema Player { name: string, score: i32, health: f64 }"
    parser = AAML.parse(content)

    schema = parser.get_schema("Player")
    assert schema.fields["name"] == "string"
    assert schema.fields["score"] == "i32"
    assert schema.fields["health"] == "f64"

def test_schema_empty_body():
    content = "@schema Empty {  }"
    parser = AAML.parse(content)
    schema = parser.get_schema("Empty")
    assert not schema.fields

def test_schema_missing_brace_error():
    with pytest.raises(ParseError):
        AAML.parse("@schema Bad name: string }")

def test_schema_missing_closing_brace_error():
    with pytest.raises(ParseError):
        AAML.parse("@schema Bad { name: string ")

def test_schema_empty_name_error():
    with pytest.raises(ParseError):
        AAML.parse("@schema { name: string }")

def test_schema_bad_field_no_colon():
    with pytest.raises(ParseError):
        AAML.parse("@schema Bad { name_string }")

def test_schema_multiple():
    content = """
        @schema Vec2 { x: f64, y: f64 }
        @schema Vec3 { x: f64, y: f64, z: f64 }
    """
    parser = AAML.parse(content)
    assert parser.get_schema("Vec2") is not None
    assert parser.get_schema("Vec3") is not None
    v3 = parser.get_schema("Vec3")
    assert "z" in v3.fields

def test_type_registers_primitive_alias():
    content = "@type age = i32"
    parser = AAML.parse(content)
    assert parser.get_type("age") is not None

def test_type_validates_valid_value():
    content = "@type count = i32"
    parser = AAML.parse(content)
    parser.validate_value("count", "42")

def test_type_validates_invalid_value():
    content = "@type count = i32"
    parser = AAML.parse(content)
    with pytest.raises(InvalidTypeError):
        parser.validate_value("count", "not_a_number")

def test_type_builtin_math():
    content = "@type position = math::vector3"
    parser = AAML.parse(content)
    parser.validate_value("position", "1.0, 2.0, 3.0")
    with pytest.raises(InvalidTypeError):
        parser.validate_value("position", "1.0, 2.0")

def test_type_builtin_physics():
    content = "@type mass = physics::kilogram"
    parser = AAML.parse(content)
    parser.validate_value("mass", "75.5")
    with pytest.raises(InvalidTypeError):
        parser.validate_value("mass", "bad")

def test_type_builtin_time():
    content = "@type created_at = time::datetime"
    parser = AAML.parse(content)
    parser.validate_value("created_at", "2024-01-15")
    with pytest.raises(InvalidTypeError):
        parser.validate_value("created_at", "bad-date")

def test_type_missing_name_error():
    with pytest.raises(ParseError):
        AAML.parse("@type = i32")

def test_type_missing_definition_error():
    with pytest.raises(ParseError):
        AAML.parse("@type mytype = ")

def test_validate_value_unknown_type():
    parser = AAML.parse("")
    with pytest.raises(InvalidTypeError):
        parser.validate_value("unknown_type", "value")

def test_schema_field_valid_type():
    content = "@schema Config { retries: i32 }\nretries = 5\n"
    parser = AAML.parse(content)
    assert parser.find_obj("retries") == "5"

def test_schema_field_invalid_type():
    content = "@schema Config { retries: i32 }\nretries = hello\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)

def test_schema_unknown_type_error():
    content = "@schema Config { speed: unicorn_type }\nspeed = 42\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)

def test_schema_string_type_always_valid():
    content = "@schema Config { name: string }\nname = hello world 123!@#\n"
    AAML.parse(content)

def test_schema_f64_valid():
    content = "@schema Config { ratio: f64 }\nratio = 3.14\n"
    AAML.parse(content)

def test_schema_f64_invalid():
    content = "@schema Config { ratio: f64 }\nratio = not_a_float\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)

def test_schema_bool_valid():
    content = "@schema Config { enabled: bool }\nenabled = true\n"
    AAML.parse(content)

def test_schema_bool_invalid():
    content = "@schema Config { enabled: bool }\nenabled = yes\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)

def test_schema_custom_type_alias_valid():
    content = "@type age = i32\n@schema Person { age: age }\nage = 25\n"
    AAML.parse(content)

def test_schema_custom_type_alias_invalid():
    content = "@type age = i32\n@schema Person { age: age }\nage = twenty-five\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)

def test_apply_schema_all_valid():
    content = "@schema Player { name: string, score: i32, health: f64 }"
    parser = AAML.parse(content)
    data = {"name": "Alice", "score": "100", "health": "98.5"}
    from aam_py.validation import apply_schema
    apply_schema(parser, "Player", data)

def test_apply_schema_missing_field():
    content = "@schema Player { name: string, score: i32 }"
    parser = AAML.parse(content)
    data = {"name": "Alice"}
    from aam_py.validation import apply_schema
    with pytest.raises(SchemaValidationError):
        apply_schema(parser, "Player", data)

def test_apply_schema_wrong_value():
    content = "@schema Player { score: i32 }"
    parser = AAML.parse(content)
    data = {"score": "not_a_number"}
    from aam_py.validation import apply_schema
    with pytest.raises(SchemaValidationError):
        apply_schema(parser, "Player", data)

def test_schema_validation_via_derive(tmp_path):
    base_file = tmp_path / "test_derive_schema_validation.aam"
    base = AAMBuilder()
    base.schema("Config", [SchemaField.required("timeout", "i32")])
    base.to_file(base_file)

    content = f"@derive {base_file}\ntimeout = not_a_number\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)

def test_derive_two_schema_selectors(tmp_path):
    base_file = tmp_path / "test_derive_two_selectors.aam"
    base = AAMBuilder()
    base.schema("SchemaA", [SchemaField.required("a_val", "i32")])
    base.schema("SchemaB", [SchemaField.required("b_val", "string")])
    base.schema("SchemaC", [SchemaField.required("c_val", "f64")])
    base.add_line("a_val", "1")
    base.add_line("b_val", "hello")
    base.to_file(base_file)

    content = f"@derive {base_file}::SchemaA::SchemaB\na_val = 42\nb_val = world\n"
    parser = AAML.parse(content)

    assert parser.get_schema("SchemaA") is not None
    assert parser.get_schema("SchemaB") is not None
    assert parser.get_schema("SchemaC") is None

def test_derive_selector_child_values_win(tmp_path):
    base_file = tmp_path / "test_derive_selector_child_wins.aam"
    base = AAMBuilder()
    base.schema("Config", [SchemaField.required("port", "i32"), SchemaField.required("host", "string")])
    base.add_line("port", "8080")
    base.add_line("host", "base-host")
    base.to_file(base_file)

    content = f"port = 9090\nhost = child-host\n@derive {base_file}::Config\n"
    parser = AAML.parse(content)

    assert parser.find_obj("port") == "9090"
    assert parser.find_obj("host") == "child-host"

def test_derive_optional_field_absent_is_ok(tmp_path):
    base_file = tmp_path / "test_derive_optional_absent.aam"
    base = AAMBuilder()
    base.schema("Config", [SchemaField.required("timeout", "i32"), SchemaField.optional("retries", "i32")])
    base.add_line("timeout", "30")
    base.to_file(base_file)

    content = f"@derive {base_file}\ntimeout = 60\n"
    parser = AAML.parse(content)

    schema = parser.get_schema("Config")
    assert schema.is_optional("retries")
    assert parser.find_obj("retries") is None

def test_derive_optional_field_present_validated(tmp_path):
    base_file = tmp_path / "test_derive_optional_valid.aam"
    base = AAMBuilder()
    base.schema("Config", [SchemaField.required("timeout", "i32"), SchemaField.optional("retries", "i32")])
    base.add_line("timeout", "30")
    base.to_file(base_file)

    content_ok = f"@derive {base_file}\ntimeout = 10\nretries = 5\n"
    AAML.parse(content_ok)

    content_bad = f"@derive {base_file}\ntimeout = 10\nretries = not_int\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content_bad)

def test_derive_nonexistent_selector_error(tmp_path):
    base_file = tmp_path / "test_derive_nonexist_selector.aam"
    base = AAMBuilder()
    base.schema("RealSchema", [SchemaField.required("x", "i32")])
    base.add_line("x", "1")
    base.to_file(base_file)

    content = f"@derive {base_file}::NonExistent\n"
    with pytest.raises(ParseError):
        AAML.parse(content)

def test_schema_nested_in_schema():
    content = """
        @schema Point  { x: f64, y: f64 }
        @schema Circle { center: Point, radius: f64 }
    """
    cfg = AAML.parse(content)
    
    ok = {"center": "{ x = 1.0, y = 2.5 }", "radius": "5.0"}
    from aam_py.validation import apply_schema
    apply_schema(cfg, "Circle", ok)

    bad_center = {"center": "{ x = not_a_float, y = 2.5 }", "radius": "5.0"}
    with pytest.raises(SchemaValidationError):
        apply_schema(cfg, "Circle", bad_center)

def test_schema_nested_optional_field_absent():
    content = """
        @schema Item   { item_name: string, item_weight: f64, item_rare*: bool }
        @schema Weapon { base: Item, damage: i32 }
    """
    cfg = AAML.parse(content)
    data = {
        "base": "{ item_name = Sword, item_weight = 2.5 }",
        "damage": "50"
    }
    from aam_py.validation import apply_schema
    apply_schema(cfg, "Weapon", data)

def test_list_of_strings_valid():
    content = "@schema Tags { name: string, items: list<string> }"
    cfg = AAML.parse(content)
    data = {"name": "my-tags", "items": "[foo, bar, baz]"}
    from aam_py.validation import apply_schema
    apply_schema(cfg, "Tags", data)

def test_list_of_i32_invalid_element():
    content = "@schema Scores { title: string, values: list<i32> }"
    cfg = AAML.parse(content)
    data = {"title": "test", "values": "[1, 2, not_int, 4]"}
    from aam_py.validation import apply_schema
    with pytest.raises(SchemaValidationError):
        apply_schema(cfg, "Scores", data)

def test_list_of_nested_schema_valid():
    content = """
        @schema Point  { x: f64, y: f64 }
        @schema Polyline { label: string, points: list<Point> }
    """
    cfg = AAML.parse(content)
    data = {
        "label": "shape",
        "points": "[{ x = 0.0, y = 0.0 }, { x = 1.0, y = 1.0 }, { x = 2.0, y = 0.0 }]"
    }
    from aam_py.validation import apply_schema
    apply_schema(cfg, "Polyline", data)

def test_list_of_nested_schema_invalid_element():
    content = """
        @schema Point  { x: f64, y: f64 }
        @schema Polyline { label: string, points: list<Point> }
    """
    cfg = AAML.parse(content)
    data = {
        "label": "bad",
        "points": "[{ x = 0.0, y = 0.0 }, { x = oops, y = 1.0 }]"
    }
    from aam_py.validation import apply_schema
    with pytest.raises(SchemaValidationError):
        apply_schema(cfg, "Polyline", data)

def test_derive_with_quoted_selector(tmp_path):
    base_file = tmp_path / "test_derive_quoted_selector.aam"
    base = AAMBuilder()
    base.schema("Quoted", [SchemaField.required("val", "string")])
    base.add_line("val", "hello")
    base.to_file(base_file)

    content = f'@derive "{base_file}"::Quoted\nval = world\n'
    parser = AAML.parse(content)

    assert parser.get_schema("Quoted") is not None
    assert parser.find_obj("val") == "world"

def test_schema_all_optional_fields():
    content = "@schema Meta { author*: string, version*: string, tags*: list<string> }"
    cfg = AAML.parse(content)
    schema = cfg.get_schema("Meta")
    assert schema.is_optional("author")
    assert schema.is_optional("version")
    assert schema.is_optional("tags")

    from aam_py.validation import apply_schema
    apply_schema(cfg, "Meta", {})

def test_derive_missing_required_field_in_child_schema(tmp_path):
    base_file = tmp_path / "test_derive_missing_required.aam"
    base = AAMBuilder()
    base.add_line("some_key", "some_val")
    base.to_file(base_file)

    content = f"@schema Required {{ must_exist: string }}\n@derive {base_file}\n"
    with pytest.raises(SchemaValidationError):
        AAML.parse(content)
