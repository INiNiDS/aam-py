import pytest
from aam_py import AAML, ParseError

TEST_CONFIG = """
    a = b
    c = d
    e = f
    d = g
    loop1 = loop2
    loop2 = loop1
"""

def test_simple_find():
    parser = AAML.parse(TEST_CONFIG)
    res = parser.find_obj("a")
    assert res is not None
    assert res == "b"

def test_not_found():
    parser = AAML.parse(TEST_CONFIG)
    assert parser.find_obj("unknown") is None

def test_deref_behavior():
    parser = AAML.parse(TEST_CONFIG)
    res = parser.find_obj("a")
    assert res is not None
    assert len(res) == 1
    assert res.startswith("b")

def test_display_trait():
    from aam_py.found_value import FoundValue
    res = FoundValue("hello")
    assert str(res) == "hello"

def test_find_deep():
    parser = AAML.parse(TEST_CONFIG)
    res = parser.find_deep("c")
    assert res is not None
    assert res == "g"

def test_find_deep_direct_loop():
    content = "key1=key1"
    aaml = AAML.parse(content)
    result = aaml.find_deep("key1")
    assert result is not None
    assert result == "key1"

def test_find_deep_indirect_loop():
    content = "a=b\nb=a"
    aaml = AAML.parse(content)
    result = aaml.find_deep("a")
    assert result is not None
    assert result == "b"

def test_find_deep_long_chain_with_loop():
    content = "start=mid\nmid=end\nend=mid"
    aaml = AAML.parse(content)
    result = aaml.find_deep("start")
    assert result is not None
    assert result == "end"

def test_find_deep_no_loop():
    content = "a=b\nb=c\nc=final"
    aaml = AAML.parse(content)
    result = aaml.find_deep("a")
    assert result is not None
    assert result == "final"

def test_parse_error_missing_equals():
    content = "invalid_line_without_equals"
    with pytest.raises(ParseError) as exc:
        AAML.parse(content)
    assert "Missing assignment operator" in str(exc.value)

def test_parse_error_empty_key():
    content = "= value"
    with pytest.raises(ParseError):
        AAML.parse(content)

def test_quotes_stripping():
    content = '''
        key1 = "value1"
        key2 = 'value2'
        key3 = value3
        key4 =
    '''
    parser = AAML.parse(content)
    assert parser.find_obj("key1") == "value1"
    assert parser.find_obj("key2") == "value2"
    assert parser.find_obj("key3") == "value3"

def test_nested_quotes_behavior():
    content = 'key = "\'inner quotes\'"'
    parser = AAML.parse(content)
    assert parser.find_obj("key") == "'inner quotes'"

def test_comments_basic():
    content = "key = value # Это комментарий"
    parser = AAML.parse(content)
    assert parser.find_obj("key") == "value"

def test_comments_inside_quotes():
    content = 'key = "value # not a comment"'
    parser = AAML.parse(content)
    assert parser.find_obj("key") == "value # not a comment"

def test_comments_mixed():
    content = '''
        key1 = "val1" # comment 1
        key2 = 'val # 2' # comment 2
        # full line comment
        key3 = val3
    '''
    parser = AAML.parse(content)
    assert parser.find_obj("key1") == "val1"
    assert parser.find_obj("key2") == "val # 2"
    assert parser.find_obj("key3") == "val3"

def test_merge_content():
    aaml = AAML()
    aaml.merge_content("a = 1")
    aaml.merge_content("b = 2")
    aaml.merge_content("a = 3")
    assert aaml.find_obj("a") == "3"
    assert aaml.find_obj("b") == "2"

def test_add_trait():
    aaml1 = AAML.parse("a = 1")
    aaml2 = AAML.parse("b = 2")
    res = aaml1 + aaml2
    assert res.find_obj("a") == "1"
    assert res.find_obj("b") == "2"

def test_add_assign_trait():
    aaml1 = AAML.parse("a = 1")
    aaml2 = AAML.parse("a = 2\nb = 3")
    aaml1 += aaml2
    assert aaml1.find_obj("a") == "2"
    assert aaml1.find_obj("b") == "3"

def test_reverse_lookup():
    content = "username = admin"
    parser = AAML.parse(content)
    assert parser.find_obj("username") == "admin"
    assert parser.find_obj("admin") == "username"

def test_empty_lines_and_whitespaces():
    content = """
        key1   =    val1
        key2=val2
    """
    parser = AAML.parse(content)
    assert parser.find_obj("key1") == "val1"
    assert parser.find_obj("key2") == "val2"

def test_missing_equals_error_details():
    content = "key_without_value"
    with pytest.raises(ParseError) as exc:
        AAML.parse(content)
    assert "Missing assignment operator" in str(exc.value)
    assert "key_without_value" in str(exc.value)

def test_deep_find_circular():
    content = "a=b\nb=c\nc=a"
    parser = AAML.parse(content)
    res = parser.find_deep("a")
    assert res is not None
    assert res == "c"
