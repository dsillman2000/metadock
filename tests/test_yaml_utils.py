import pytest

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
    ],
)
def test_yaml_utils__flatten_merge_keys(yml_dict, flat_dict):
    assert yaml_utils.flatten_merge_keys(yml_dict) == flat_dict
