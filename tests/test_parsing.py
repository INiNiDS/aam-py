from aam_py.parsing import strip_comment, is_inline_object, parse_inline_object

def test_color_not_stripped():
    assert strip_comment("tint = #ff6600") == "tint = #ff6600"
    assert strip_comment("tint=#ff6600") == "tint=#ff6600"

def test_comment_after_space_stripped():
    assert strip_comment("key = value # comment").strip() == "key = value"

def test_quoted_hash_preserved():
    s = r'key = "val # not comment"'
    assert strip_comment(s) == s

def test_inline_object_parsed():
    result = dict(parse_inline_object("{ x = 1.0, y = 2.0 }"))
    assert len(result) == 2
    assert result.get("x") == "1.0"
    assert result.get("y") == "2.0"

def test_inline_object_colon_separator():
    result = dict(parse_inline_object("{ name: Alice, score: 100 }"))
    assert result.get("name") == "Alice"
    assert result.get("score") == "100"

def test_inline_object_quoted_values():
    result = dict(parse_inline_object(r'{ name = "Alice Doe", active = true }'))
    assert result.get("name") == "Alice Doe"

def test_is_inline_object_detection():
    assert is_inline_object("{ x = 1 }") is True
    assert is_inline_object("[1, 2, 3]") is False
    assert is_inline_object("hello") is False

def test_inline_object_nested_preserves_commas():
    result = dict(parse_inline_object("{ base = { x = 1, y = 2 }, z = 3 }"))
    assert len(result) == 2
    assert result.get("base") == "{ x = 1, y = 2 }"
    assert result.get("z") == "3"

def test_inline_object_nested_list_value():
    result = dict(parse_inline_object("{ tags = [a, b, c], name = test }"))
    assert len(result) == 2
    assert result.get("tags") == "[a, b, c]"
