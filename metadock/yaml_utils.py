from typing import Any


def flatten_merge_keys(yaml_dict: Any) -> dict:
    """Flatten the merge keys ("<<") in a nested dictionary object.

    Args:
        yaml_dict (Any): Object whose merge keys will be flattened

    Returns:
        dict: Flattened representation of the nested dictionary object
    """
    if not isinstance(yaml_dict, dict):
        return yaml_dict  # type: ignore

    flattened_yaml_dict = {}

    for key in yaml_dict.keys():
        flat_yaml_value = flatten_merge_keys(yaml_dict[key])
        if key == "<<":
            flattened_yaml_dict |= flat_yaml_value
        else:
            flattened_yaml_dict[key] = flat_yaml_value

    return flattened_yaml_dict
