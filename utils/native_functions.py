from utils.exceptions import Fault
import utils.lookup as lookup

from utils.parser import Value

def native_print(args: list[Value]) -> Value:
    if len(args) < 1:
        raise Fault(lookup.FaultType.NATIVE_FUNCTION_ARGS)
    for index, value in enumerate(args):
        end_value = ' ' if index < len(args) - 1 else None
        print(wrapper_value(value), end=end_value)
    return Value(
        value_type=lookup.NONE,
        value=None
    )

def native_input(args: list[Value]) -> Value:
    if len(args) != 0:
        raise Fault(lookup.FaultType.NATIVE_FUNCTION_ARGS)
    inp = input()
    return Value(
        value_type=lookup.STRING,
        value=inp
    )

def native_len(args: list[Value]) -> Value:
    if len(args) != 1:
        raise Fault(lookup.FaultType.NATIVE_FUNCTION_ARGS)
    value: Value = args[0]
    if value.value_type not in {lookup.LIST, lookup.STRING}:
        raise Fault(lookup.FaultType.TYPE_ERROR)
    return Value(
        value_type=lookup.INTEGER,
        value=len(args[0].value)
    )

def wrapper_value(value: Value) -> any:
    wrapper_lookup = {
        lookup.INTEGER: value.value,
        lookup.STRING: value.value,
        lookup.NONE: "null",
        lookup.BOOLEAN: "true" if value.value == 1 else "false",
    }
    if value.value_type == lookup.LIST:
        list_data = [wrapper_value(item) for item in value.value]
        return list_data
    elif value.value_type in wrapper_lookup:
        return wrapper_lookup[value.value_type]
    else:
        return f"<type({value.value_type}): {value.value}>"


def get_all_native() -> dict:
    return {
        "print": native_print,
        "input": native_input,
        "len": native_len
    }
