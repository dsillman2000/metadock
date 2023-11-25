import string
from pathlib import Path

import pytest
import yaml

from metadock import yaml_utils


@pytest.mark.parametrize(
    "yml_dict,flat_dict",
    [
        pytest.param(
            {"name": "foo", "value": "bar"},
            {"name": "foo", "value": "bar"},
            id="simple 1-level dict",
        ),
        pytest.param(
            "non-dictionary",
            "non-dictionary",
            id="simple non-dictionary string",
        ),
        pytest.param(
            ["a", "b", "c"],
            ["a", "b", "c"],
            id="simple flat list",
        ),
        pytest.param(
            {"<<": {"key": "value"}},
            {"key": "value"},
            id="simple 1 level to flatten",
        ),
        pytest.param(
            {"<<": {"key": "value"}, "first": "level"},
            {"key": "value", "first": "level"},
            id="simple 1 level to flatten with adjacent key",
        ),
        pytest.param(
            {"<<": {"key": "value", "<<": {"inner": "item"}}, "first": "level"},
            {"key": "value", "inner": "item", "first": "level"},
            id="simple 2 level to flatten with adjacent key",
        ),
        pytest.param(
            {"<<": [{"key_a": "value"}, {"key_b": "value again"}], "first": "level"},
            {"key_a": "value", "key_b": "value again", "first": "level"},
            id="simple merge list",
        ),
        pytest.param(
            {"<<": [{"k": "value"}, {"k": "value again"}], "first": "level"},
            {"k": "value again", "first": "level"},
            id="simple merge list with collision",
        ),
    ],
)
def test_yaml_utils__flatten_merge_keys(yml_dict, flat_dict):
    assert yaml_utils.flatten_merge_keys(yml_dict) == flat_dict


@pytest.mark.parametrize(
    "contents,key,value",
    [
        pytest.param(
            "name: foo",
            "name",
            "foo",
            id="simple single-key dict",
        ),
        pytest.param(
            "name: foo\nvalue: bar",
            "value",
            "bar",
            id="simple 2-key dict",
        ),
        pytest.param(
            "name: \n  x: 32\n  y: 64",
            "name",
            {"x": "32", "y": "64"},
            id="simple full dict query",
        ),
        pytest.param(
            "name: \n  x: 32\n  y: 64",
            "name.x",
            "32",
            id="simple dict key query",
        ),
    ],
)
def test_yaml_utils__import_key(tmp_path, contents, key, value):
    (tmp_path / "test.yml").write_text(contents)
    assert yaml_utils.import_key(tmp_path, Path("test.yml"), key) == value


def test_yaml_utils__resolve_all_imports(tmp_path):
    (tmp_path / "misc.yml").write_text("et_cetera:\n  first_value: David\n  second_value: Excelsior")

    (tmp_path / "test1.yml").write_text("test:\n  <<: { import: misc.yml, key: et_cetera.second_value }")
    test_1_contents = yaml_utils.flatten_merge_keys(yaml.safe_load((tmp_path / "test1.yml").read_text()))

    assert yaml_utils.resolve_all_imports(tmp_path, test_1_contents) == {"test": "Excelsior"}

    (tmp_path / "test2.yml").write_text("test:\n  <<: { import: misc.yml, key: et_cetera }")
    test_2_contents = yaml_utils.flatten_merge_keys(yaml.safe_load((tmp_path / "test2.yml").read_text()))

    assert yaml_utils.resolve_all_imports(tmp_path, test_2_contents) == {
        "test": {"first_value": "David", "second_value": "Excelsior"}
    }

    (tmp_path / "test3.yml").write_text("test:\n  <<: { import: misc.yml }")
    test_2_contents = yaml_utils.flatten_merge_keys(yaml.safe_load((tmp_path / "test3.yml").read_text()))

    assert yaml_utils.resolve_all_imports(tmp_path, test_2_contents) == {
        "test": {"et_cetera": {"first_value": "David", "second_value": "Excelsior"}}
    }
