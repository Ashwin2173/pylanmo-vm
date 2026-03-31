import utils.lookup as lookup

from utils.exceptions import Fault
from utils.parser import Function, Value, OpCode
from utils.lookup import FaultType

class VM:
    def __init__(self, symbol_table: list[Value], function_table: dict[str, Function]):
        self.function_table = function_table
        self.symbol_table: list[Value] = symbol_table

        self.stack: list[Value] = list()
        self.frames: list[Frame] = list()
        self.globals: dict[str, Value] = dict()
        self.op_code_lookup: dict[int, callable] = {
            lookup.OP_PUSH: self.__push,
            lookup.OP_POP: self.__pop,
            lookup.OP_BIN: self.__bin_op,
            lookup.OP_PEEK: self.__peek,
            lookup.OP_CALL: self.__call,
            lookup.OP_RET: self.__ret
        }
        self.op_bin_op_lookup = {
            lookup.BIN_OP_ADD: self.__add
        }

    def step_in(self):
        if len(self.frames) == 0:
            raise Fault(FaultType.DONE)
        frame: Frame = self.__get_current_frame()
        if frame.ip >= len(frame.func.body):
            raise Fault(FaultType.NO_RET)
        current_op: OpCode = frame.func.body[frame.ip]
        if current_op.op_code not in self.op_code_lookup:
            raise NotImplementedError(f"op_code lookup for opcode: {current_op.op_code}")
        self.op_code_lookup[current_op.op_code](current_op.data)
        frame.ip += 1

    def load_main(self):
        self.stack.append(Value(lookup.FUNCTION, "main"))
        self.__load_function(0)

    def __load_function(self, args: int) -> None:
        name = self.stack[-args - 1]
        func: Function = self.function_table.get(name.value)
        if func is None:
            raise Fault(FaultType.UNDEFINED_FUNCTION)
        self.frames.append(Frame(
            func = func,
            base_pointer = len(self.stack) - args
        ))

    def __get_current_frame(self):
        if len(self.frames) == 0:
            raise Fault(FaultType.NO_FRAME)
        return self.frames[-1]

    def __push(self, value: int) -> None:
        value: Value = self.symbol_table[value]
        self.stack.append(value)

    def __pop(self, _=None) -> Value:
        self.__check_stack_underflow()
        return self.stack.pop()

    def __bin_op(self, operation_value: int) -> None:
        if operation_value not in self.op_bin_op_lookup:
            raise Fault(FaultType.INVALID_BIN_OP)
        self.op_bin_op_lookup[operation_value]()

    def __add(self, _=None) -> None:
        right: Value = self.__pop()
        left: Value = self.__pop()
        if left.value_type == lookup.STRING or right.value_type == lookup.STRING:
            self.stack.append(Value(lookup.STRING, f"{left.value}{right.value}"))
        elif left.value_type == lookup.INTEGER and right.value_type == lookup.INTEGER:
            self.stack.append(Value(lookup.INTEGER, left.value + right.value))
        else:
            raise Fault(FaultType.TYPE_ERROR)

    def __peek(self, _=None) -> None:
        self.__check_stack_underflow()
        peek = self.stack[-1]
        if peek.value_type in {lookup.INTEGER, lookup.STRING}:
            print(peek.value)
            return
        print(f"<type({peek.value_type}): {peek.value}>")

    def __call(self, count: int) -> None:
        self.__check_stack_underflow()
        if len(self.stack) < count:
            raise Fault(FaultType.STACK_UNDERFLOW)
        if self.stack[-count-1].value_type != lookup.FUNCTION:
            raise Fault(FaultType.OUT_OF_ORDER)
        self.__load_function(count)

    def __ret(self, _=None) -> None:
        frame = self.__get_current_frame()
        return_value = self.__pop()
        self.stack = self.stack[:frame.base_pointer - 1]
        self.stack.append(return_value)
        self.frames.pop()

    def __check_stack_underflow(self):
        frame = self.__get_current_frame()
        if len(self.stack) <= frame.base_pointer:
            raise Fault(FaultType.STACK_UNDERFLOW)

class Frame:
    def __init__(self, func: Function, base_pointer: int):
        self.func = func
        self.ip = 0
        self.base_pointer = base_pointer
