import re
from typing import Dict
from typing import List


def parse_dict_and_list(hub, state_id: str, data: Dict or List, keys: List):
    """
    Traverse a dict or list using a colon-delimited (or otherwise delimited,
    using the 'delimiter' param) target string. The target 'foo:bar:0' will
    return data['foo']['bar'][0] if this value exists, and will otherwise
    return the dict in the default argument.
    List resolution - The target 'foo:bar:[0]' or 'foo:bar[0]' will return data['foo']['bar'][0] if data
    like {'foo':{'bar':['baz']}}
    Dict resolution - The target 'foo:bar:0' will return data['foo']['bar'][0] if data like
    {'foo':{'bar':{'0':'baz'}}}
    """

    try:
        ref_path = ":".join(keys)
        ptr = data
        for key in keys:
            key_to_parse, indexes = hub.tool.idem.arg_bind_utils.parse_index(key)
            if isinstance(ptr, list):
                if key_to_parse:
                    ptr = [parse_dict(hub, item, key_to_parse, indexes) for item in ptr]
                else:
                    # If argument binding contains a nested collection, find the element in the collection, ex arg[0][1][2]
                    ptr = hub.tool.idem.arg_bind_utils.get_chunk_with_index(
                        ptr, indexes, ref_path
                    )
            else:
                ptr = parse_dict(hub, ptr, key_to_parse, indexes)
    except ValueError as ex:
        raise ValueError(f'"Failed to parse "{ref_path}" for state "{state_id}". {ex}')
    return ptr


def parse_dict(hub, data: Dict, key_to_parse: str, indexes: List):
    ptr = data
    if key_to_parse:
        if key_to_parse not in ptr:
            raise ValueError(
                f'Key "{key_to_parse}" is not found as part of the state "new_state".'
            )
        ptr = ptr[key_to_parse]
        # If argument binding contains a nested collection, find the element in the collection, ex arg[0][1][2]
        ptr = hub.tool.idem.arg_bind_utils.get_chunk_with_index(
            ptr, indexes, key_to_parse
        )

    return ptr


async def find_arg_reference_data(hub, arg_bind_expr: str):
    """
    Resolve ${cloud:state:attribute_path} expressions to a value used in jinja using the hub's RUNNING dictionary
    """

    state_data = None

    run_name = hub.idem.RUN_NAME

    arg_bind_arr = arg_bind_expr.split(":")

    if len(arg_bind_arr) < 2:
        hub.log.debug(
            f" arg-bind expression `{arg_bind_expr}` doesn't comply with standards. Expected format is "
            f"$'{'resource_state:resource_name:attribute-path'}'  "
        )
        return state_data, False

    state_id = arg_bind_arr[1]

    attribute_path = None

    if len(arg_bind_arr) > 2:
        """
        From the arg-bind template - ${cloud:state:[0]:attribute:[1]} , get the attribute path [0]:attribute:[1]
        which will be used to resolve the correct value from the new_state.
        """
        attribute_path = arg_bind_arr[2:]

    run_data = hub.idem.RUNS.get(run_name, None)
    low_data = None
    if run_data:
        low_data = run_data.get("low", None)

    tag = None
    if low_data:
        for low in low_data:
            if "__id__" in low and low["__id__"] == state_id:
                chunk = {
                    "__id__": state_id,
                    "name": low.get("name"),
                    "state": low.get("state"),
                    "fun": low.get("fun"),
                }
                tag = hub.idem.tools.gen_tag(chunk)
                break

    arg_bind_template = "${" + arg_bind_expr[0] + "}"

    if not tag:
        hub.log.debug(
            f"Could not parse `{arg_bind_expr}` in jinja. The data for arg_binding reference `{arg_bind_template}` "
            f"could not be found on the hub. "
        )
        return state_data, False

    if run_data:
        executed_states = run_data.get("running", None)
        if executed_states is not None and tag in executed_states:
            state_data = executed_states.get(tag).get("new_state", None)
            if state_data and attribute_path:
                state_data = hub.tool.idem.arg_bind_utils.parse_dict_and_list(
                    state_id, state_data, attribute_path
                )

    return state_data, True


def parse_index(hub, key_to_parse):
    """
    Parse indexes of key. For example, test[0][1][*] will return "test" as parsed key and [0,1,*] as parsed indexes.
    """
    # Handle the case when dictionary references in the key definition are escaped, ex test[//0][//1]
    indexes = re.findall(r"\[[^\]\\]*]", key_to_parse)
    if indexes:
        parsed_indexes = []
        for index in indexes:
            parsed_index = index[1 : len(index) - 1]
            if not parsed_index.isdigit() and parsed_index != "*":
                raise ValueError(
                    f'Cannot parse argument value for key "{key_to_parse}" for index "{parsed_index}", because "{parsed_index}" is not supported".'
                )
            parsed_indexes.append(parsed_index)

        return key_to_parse[0 : key_to_parse.index("[")], parsed_indexes

    return key_to_parse, None


def get_chunk_with_index(hub, chunk, indexes, arg_key):
    if indexes:
        index = indexes[0]
        if index.isdigit():
            index = int(index)
            if not isinstance(chunk, list) or len(chunk) < index + 1:
                raise ValueError(
                    f'Cannot parse argument value for key "{arg_key}" and index "{index}", '
                    f'because argument value is not a list or it does not include element with index "{index}".'
                )
            chunk = chunk[index]
            return get_chunk_with_index(hub, chunk, indexes[1:], arg_key)
        elif index == "*":
            if not isinstance(chunk, list):
                raise ValueError(
                    f'Cannot parse argument value for key "{arg_key}" for index "{index}", '
                    f"because argument key is not a list."
                )
            chunks = [
                get_chunk_with_index(hub, item, indexes[1:], arg_key) for item in chunk
            ]
            return chunks
        else:
            raise ValueError(
                f'Cannot parse argument value for key "{arg_key}" for index "{index}", because "{index}" is not supported".'
            )

    return chunk
