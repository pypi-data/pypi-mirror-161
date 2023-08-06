from typing import Any
from typing import Dict


def check(
    hub,
    name: str,
    ctx: Dict[str, Any],
    condition: Any,
    reqret: Dict[str, Any],
    chunk: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Parse argument binding reference and update the chunk argument with the requisite value.
    For example:
    - arg_bind:
        - cloud:
            - referenced_state:
                - referenced_state_property: this_state_property
    """
    if condition != "arg_bind":
        return {"errors": [f'"{condition}" is not a supported arg resolver.']}

    if not isinstance(reqret.get("args", {}), list):
        return {"errors": [f'"{condition}" is not in a supported format.']}

    # TODO: Add debug logging
    # Iterate over args of the "arg_bind" requisite, each arg is an argument binding
    for req_def in reqret.get("args", []):
        # Validate that requisite definition is a key/value pair,
        # where the key is the referenced state argument path
        # and the value is the current state argument path
        if not isinstance(req_def, dict):
            return {"errors": [f'"{req_def}" is not in a supported format.']}
        req_key_path = next(iter(req_def))
        chunk_key_path = req_def[req_key_path]
        resource_state = reqret.get("state")
        resource_name = reqret.get("name")

        if reqret["ret"].get("new_state", None) is None:
            return {
                "errors": [
                    f'"{resource_state}:{resource_name}" state does not have "new_state" in the state returns.'
                ]
            }

        # Construct state argument reference definition based on arg_bind requisite
        arg_reference_def = (
            "${" + f"{resource_state}:{resource_name}:{req_key_path}" + "}"
        )

        try:
            # First, find the value of the referenced state argument, based on the path
            # Iterate over referenced state argument key chain and find the value in the state "new_state"
            req_arg_value = hub.tool.idem.arg_bind_utils.parse_dict_and_list(
                resource_state, reqret["ret"]["new_state"], req_key_path.split(":")
            )

            # Second, set current state argument to the referenced state argument value
            hub.log.debug(
                f"Replacing references to `{arg_reference_def}` with value `{req_arg_value}`"
            )

            hub.idem.rules.arg_resolver.set_chunk_arg_value(
                chunk,
                arg_reference_def,
                chunk_key_path.split(":"),
                req_arg_value,
                None,
            )
        except IndexError as ex:
            return {"errors": [f"{ex}"]}
        except ValueError as ex:
            return {"errors": [f"{ex}"]}

    return {}


def set_chunk_arg_value(
    hub, chunk, arg_reference_def, arg_key_chain, arg_value, chunk_indexes
):
    """
    Recursively iterate over arg_keys and update the chunk desired key with the referenced value
    """
    arg_key = arg_key_chain.pop(0)
    arg_key, next_chunk_indexes = hub.tool.idem.arg_bind_utils.parse_index(arg_key)
    # Unescape dictionary references in the key definition.
    arg_key = arg_key.replace("[\\", "[")

    if len(arg_key_chain) == 0:
        indexed_chunk = hub.tool.idem.arg_bind_utils.get_chunk_with_index(
            chunk, chunk_indexes, arg_key
        )

        if next_chunk_indexes:
            # arg_key is set to a (nested) collection and arg_value is added to it , ex: arg_key[0][1][2]
            _set_chunk_with_index(
                indexed_chunk[arg_key], next_chunk_indexes, arg_reference_def, arg_value
            )
        else:
            if arg_key not in indexed_chunk:
                indexed_chunk[arg_key] = ""
            # arg_key is set to arg_value
            indexed_chunk[arg_key] = _replace_arg_reference_with_arg_value(
                indexed_chunk[arg_key], arg_reference_def, arg_value
            )

    else:
        chunk = hub.tool.idem.arg_bind_utils.get_chunk_with_index(
            chunk, chunk_indexes, arg_key
        )
        if arg_key not in chunk:
            chunk[arg_key] = {}

        hub.idem.rules.arg_resolver.set_chunk_arg_value(
            chunk[arg_key],
            arg_reference_def,
            arg_key_chain,
            arg_value,
            next_chunk_indexes,
        )


def _set_chunk_with_index(chunk, chunk_indexes, arg_reference_def, arg_value):
    index = chunk_indexes.pop(0)
    if not index.isdigit():
        raise ValueError(
            f'Cannot set argument value for index "{index}". The "{index}" is not supported'
        )
    index = int(index)
    if not isinstance(chunk, list) or len(chunk) < index + 1:
        raise ValueError(
            f'Cannot set argument value for index "{index}", '
            f'because argument key is not a list or it does not include element with index "{index}".'
        )

    if len(chunk_indexes) == 0:
        chunk[index] = _replace_arg_reference_with_arg_value(
            chunk[index], arg_reference_def, arg_value
        )
    else:
        _set_chunk_with_index(chunk[index], chunk_indexes, arg_reference_def, arg_value)


def _replace_arg_reference_with_arg_value(
    chunk_arg_value, arg_reference_def, arg_value
):
    """
    Find all occurrences of arg_reference_def in chunk_arg_value and replace them with arg_value.
    Return chunk_arg_value with all references to arg_reference_def resolved, or arg_value if no
    references found.
    """
    if (
        chunk_arg_value
        and isinstance(chunk_arg_value, str)
        and isinstance(arg_value, str)
        and arg_reference_def in chunk_arg_value
    ):
        return str.replace(chunk_arg_value, arg_reference_def, arg_value)
    else:
        return arg_value
