import os
import pytest
from aam_py import AAML, AAMBuilder, ParseError

def test_parse_error_missing_equals():
    content = "invalid_line_without_equals"
    with pytest.raises(ParseError):
        AAML.parse(content)

def test_parse_error_empty_key():
    content = "= value"
    with pytest.raises(ParseError):
        AAML.parse(content)

def test_import_functionality(tmp_path):
    sub_file = tmp_path / "test_sub_config.aam"
    b = AAMBuilder()
    b.add_line("sub_key", "sub_value")
    b.to_file(sub_file)

    content = f"main_key = main_value\n@import {sub_file}"
    parser = AAML.parse(content)
    
    assert parser.find_obj("main_key") == "main_value"
    assert parser.find_obj("sub_key") == "sub_value"

def test_recursive_import(tmp_path):
    file1 = tmp_path / "rec_import_1.aam"
    file2 = tmp_path / "rec_import_2.aam"

    b1 = AAMBuilder()
    b1.import_path(str(file2))
    b1.add_line("key1", "val1")
    b1.to_file(file1)

    b2 = AAMBuilder()
    b2.add_line("key2", "val2")
    b2.to_file(file2)

    parser = AAML.load(str(file1))

    assert parser.find_obj("key1") == "val1"
    assert parser.find_obj("key2") == "val2"

def test_import_with_quotes(tmp_path):
    sub_file = tmp_path / "quoted_import.aam"
    b = AAMBuilder()
    b.add_line("q_key", "q_val")
    b.to_file(sub_file)

    content = f'@import "{sub_file}"'
    parser = AAML.parse(content)

    assert parser.find_obj("q_key") == "q_val"
