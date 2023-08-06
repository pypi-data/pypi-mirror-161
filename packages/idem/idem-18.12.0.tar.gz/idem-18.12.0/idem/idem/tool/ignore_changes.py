import inspect
import re
from typing import Dict
from typing import List


def ignore_parameter_changes(
    hub,
    ignore_changes: List,
    params: Dict,
    param_signatures: Dict[str, inspect.Parameter],
):
    """
    Set an optional parameter within params to None according to the parameter path in ignore_changes. For example,
    path key1:key2 path will result to {key1: {key2: None}}
    :param ignore_changes: A list of path of parameters that will be assigned to None value
                           to ignore being updated in present().
    :param params: A dict of parameter-value pairs.
    :param param_signatures: A dict containing the parameter signatures.
    """
    for param_path in ignore_changes:
        # Split the path with ":"
        path = param_path.split(":")
        arg_key, indexes = _parse_index(path[0])
        if arg_key in ["hub", "ctx", "name"]:
            continue
        # We can only assigning None to the optional parameters which default is not inspect._empty
        if (
            arg_key in param_signatures
            and param_signatures.get(arg_key).default != inspect._empty
        ):
            try:
                _nullify_parameter(parent=params, indexes=[], remaining_keys=path)
            except Exception as e:
                hub.log.warning(
                    f"Error when processing ignore_changes parameter path {param_path}: {e.__class__.__name__} {e}"
                )


def _parse_index(key_to_parse):
    """
    Parse indexes of key. For example, test[0][1] will return "test" as parsed key and [0,1] as parsed indexes.
    test[0][*] will return 'test' as parsed key and [0, '*'] as the parsed indexes.
    """
    rule = r"\[\d+\]|\[\*\]"
    indexes = re.findall(rule, key_to_parse)
    if indexes:
        index_digits = []
        for index in indexes:
            if "[*]" == index:
                index_digits.append("*")
            else:
                index_digit = re.search(r"\d+", index).group(0)
                index_digits.append(int(index_digit))

        return key_to_parse[0 : key_to_parse.index("[")], index_digits

    return key_to_parse, None


def _nullify_parameter(parent: Dict or List, indexes: List, remaining_keys: List):
    """
    Go through a dictionary or list according to the path and replace the destination value with None.
    For example, if path is a:b, params {"a": {"b": "value"}} will become {"a": {"b": None}}
    :param parent: A Dict or List collection that contains the data to be set to None
    :param indexes: A list that contains the sequence of indexes to be traversed if the parent is a list
    :param remaining_keys: a List of remaining keys that need to be traversed.
    """
    # If there is no remaining keys, then we are in the last part of a parameter path
    if (not remaining_keys) and indexes:
        # If indexes is not empty, parent should be a List type collection, which allows us to traverse it with the indexes
        if len(indexes) == 1:
            # If indexes only has one index left, then we we can just replace the value at the index with None
            if isinstance(indexes[0], int):
                parent[indexes[0]] = None
            else:
                raise ValueError(f"Invalid index {indexes[0]} at the end.")
        else:
            # Traverse the param data according to the indexes
            if isinstance(indexes[0], int):
                _nullify_parameter(parent[indexes[0]], indexes[1:], [])
            # If '*' is in the index, then we traverse into all elements of the list
            elif indexes[0] == "*":
                for element in parent:
                    _nullify_parameter(element, indexes[1:], [])
            else:
                raise ValueError(f"Invalid index {indexes[0]}")
    elif indexes:
        # If indexes exists, parent should be a List type collection. We traverse it with the indexes
        if isinstance(indexes[0], int):
            _nullify_parameter(
                parent[indexes[0]],
                indexes[1:] if len(indexes) > 1 else [],
                remaining_keys,
            )
        elif indexes[0] == "*":
            for element in parent:
                _nullify_parameter(
                    element, indexes[1:] if len(indexes) > 1 else [], remaining_keys
                )
        else:
            raise ValueError(f"Invalid index {indexes[0]}")
    else:
        # If indexes is empty, we can move forward to process the next element in remaining_keys, which holds the
        # remaining parameter path
        arg_key, indexes = _parse_index(remaining_keys[0])
        if len(remaining_keys) == 1 and not indexes:
            # If the remaining key is one, and there is no index in the key, then this is the last key in the data
            # so we can just override it with None
            parent[arg_key] = None
        else:
            _nullify_parameter(
                parent[arg_key],
                indexes,
                remaining_keys[1:] if len(remaining_keys) else [],
            )
