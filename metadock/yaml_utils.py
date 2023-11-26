import operator
from functools import reduce
from pathlib import Path
from typing import Any, Optional

import yaml

from metadock import exceptions


def flatten_merge_keys(yaml_dict: Any) -> dict:
    """Flatten the merge keys ("<<") in a nested dictionary object.

    Args:
        yaml_dict (Any): Object whose merge keys will be flattened

    Returns:
        dict: Flattened representation of the nested dictionary object
    """
    if isinstance(yaml_dict, list):
        return [flatten_merge_keys(el) for el in yaml_dict]

    if not isinstance(yaml_dict, dict):
        return yaml_dict  # type: ignore

    flattened_yaml_dict = {}

    for key in yaml_dict.keys():
        flat_yaml_value = flatten_merge_keys(yaml_dict[key])
        if key == "<<":
            if isinstance(flat_yaml_value, list):
                flattened_yaml_dict |= reduce(operator.or_, flat_yaml_value, {})
            elif isinstance(flat_yaml_value, dict):
                flattened_yaml_dict |= flat_yaml_value
        else:
            flattened_yaml_dict[key] = flat_yaml_value

    return flattened_yaml_dict


def import_key(root_path: Path, relative_path: Path, key: Optional[str] = None) -> Any:
    """Try to import an alias from the root path with the given name.

    Args:
        root_path (Path): Absolute path to the Metadock project's content_schematics directory
        relative_path (Path): Relative path to the external file
        key (Optional[str]): Key path to resolve, or None to return the entire file

    Raises:
        exceptions.MetadockYamlImportError: Imported key / file could not be resolved

    Returns:
        Any: Fully resolved yaml source from the external file
    """

    if not (root_path / relative_path).exists():
        raise exceptions.MetadockYamlImportError(f"Could not find import path '{root_path}'")

    if not (root_path / relative_path).is_file():
        raise exceptions.MetadockYamlImportError(f"Import path '{root_path}' is not a file")

    contents: dict[str, Any] = yaml.load((root_path / relative_path).read_text(), yaml.BaseLoader)
    if key is not None:
        contents = reduce(lambda acc, el: acc[el], key.split("."), contents)
    return resolve_all_imports(root_path, contents)


def resolve_all_imports(root_path: Path, yaml_obj: Any) -> Any:
    """Recursively resolve all imports in a yaml object.

    Args:
        root_path (Path): Root path to resolve the imports
        yaml_obj (Any): Yaml object with imports to resolve

    Raises:
        exceptions.MetadockYamlImportError: One or more import could not be resolved

    Returns:
        Any: Yaml object with imports resolved
    """
    if isinstance(yaml_obj, list):
        return [resolve_all_imports(root_path, el) for el in yaml_obj]

    if not isinstance(yaml_obj, dict):
        return yaml_obj  # type: ignore

    if set(yaml_obj.keys()) in ({"import"}, {"import", "key"}):
        return import_key(root_path, yaml_obj["import"], yaml_obj.get("key", None))

    resolved_subdict: dict[str, Any] = {}

    for key in yaml_obj.keys():
        resolved_subdict[key] = resolve_all_imports(root_path, yaml_obj[key])

    return resolved_subdict
