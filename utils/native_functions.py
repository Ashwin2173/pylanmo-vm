from utils.exceptions import Fault
import utils.lookup as lookup

from utils.parser import Value

def native_print(args: list[Value]) -> Value:
    if len(args) < 1:
        raise Fault(lookup.FaultType.NATIVE_FUNCTION_ARGS)
    for index, value in enumerate(args):
        end_value = ' ' if index < len(args) - 1 else None
        wrapper_value = {
            lookup.INTEGER: value.value,
            lookup.STRING: value.value,
            lookup.NONE: "null",
            lookup.BOOLEAN: "true" if value.value == 1 else "false"
        }
        if value.value_type in wrapper_value:
            print(wrapper_value[value.value_type], end=end_value)
        else:
            print(f"<type({value.value_type}): {value.value}>", end=end_value)
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

def get_all_native() -> dict:
    return {
        "print": native_print,
        "input": native_input
    }
