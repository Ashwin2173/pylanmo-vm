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
        self.memory: list[Value] = list()
        self.op_code_lookup: dict[int, callable] = {
            lookup.OP_PUSH: self.__push,
            lookup.OP_POP:  self.__pop,
            lookup.OP_BIN:  self.__bin_op,
            lookup.OP_WRITE: self.__write,
            lookup.OP_CALL: self.__call,
            lookup.OP_RET:  self.__ret,
            lookup.OP_JUMP: self.__jump,
            lookup.OP_JUMP_IF_FALSE: self.__jump_if_false,
            lookup.OP_DUP: self.__dup,
            lookup.OP_STORE: self.__store,
            lookup.OP_LOAD: self.__load,
            lookup.OP_MAKE_LIST: self.__make_list,
            lookup.OP_GET_INDEX: self.__get_index,
            lookup.OP_SET_INDEX: self.__set_index,
        }
        self.op_bin_int = {
            lookup.BIN_OP_ADD: lambda x, y: y + x,
            lookup.BIN_OP_SUB: lambda x, y: y - x,
            lookup.BIN_OP_MUL: lambda x, y: y * x,
            lookup.BIN_OP_DIV: lambda x, y: y / x,
            lookup.BIN_OP_MOD: lambda x, y: y % x,
        }
        self.op_bin_cmp = {
            lookup.BIN_OP_EEQ: lambda x, y: y == x,
            lookup.BIN_OP_NEQ: lambda x, y: y != x,
            lookup.BIN_OP_GEQ: lambda x, y: y >= x,
            lookup.BIN_OP_GTN: lambda x, y: y >  x,
            lookup.BIN_OP_LEQ: lambda x, y: y <= x,
            lookup.BIN_OP_LTN: lambda x, y: y <  x,

            lookup.BIN_OP_AND: lambda x, y: y and x,
            lookup.BIN_OP_OR:  lambda x, y: y or  x
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
        if "main" not in self.function_table:
            raise Fault(FaultType.UNDEFINED_FUNCTION)
        self.stack.append(Value(lookup.FUNCTION, self.function_table["main"]))
        self.__load_function(0)

    def __load_function(self, args: int) -> None:
        func_value: Value = self.stack[-args - 1]
        if func_value.value_type != lookup.FUNCTION:
            raise Fault(FaultType.TYPE_ERROR)
        function: Function = func_value.value
        if function.is_native:
            self.__call_native_function(function, args)
            return
        self.frames.append(Frame(
            func = function,
            base_pointer = len(self.stack) - args,
            mem_base_pointer = len(self.memory)
        ))
        self.memory += [None for _ in range(function.local_count)]

    def __get_current_frame(self):
        if len(self.frames) == 0:
            raise Fault(FaultType.NO_FRAME)
        return self.frames[-1]

    def __push(self, value: int) -> None:
        value: Value = self.symbol_table[value]
        if value.value_type == lookup.FUNCTION:
            if value.value not in self.function_table:
                raise Fault(FaultType.UNDEFINED_FUNCTION)
            value: Value = Value(lookup.FUNCTION, self.function_table[value.value])
        self.stack.append(value)

    def __pop(self, _=None) -> Value:
        self.__check_stack_underflow()
        return self.stack.pop()

    def __bin_op(self, operation_value: int) -> None:
        if operation_value == lookup.BIN_OP_ADD:
            self.__bin_op_add()
        elif operation_value in self.op_bin_int:
            self.__bin_op_int(operation_value)
        elif operation_value in self.op_bin_cmp:
            self.__bin_op_cmp(operation_value)
        else:
            raise Fault(FaultType.INVALID_BIN_OP)

    def __bin_op_add(self) -> None:
        right: Value = self.__pop()
        left: Value = self.__pop()
        if left.value_type == lookup.STRING or right.value_type == lookup.STRING:
            result = f"{left.value}{right.value}"
            self.stack.append(Value(lookup.STRING, result))
        elif left.value_type == lookup.INTEGER and right.value_type == lookup.INTEGER:
            result = self.op_bin_int[lookup.BIN_OP_ADD](left.value, right.value)
            self.stack.append(Value(lookup.INTEGER, result))
        else:
            raise Fault(FaultType.TYPE_ERROR)

    def __bin_op_int(self, op_value: int) -> None:
        right: Value = self.__pop()
        left: Value = self.__pop()
        if left.value_type != lookup.INTEGER or right.value_type != lookup.INTEGER:
            raise Fault(FaultType.TYPE_ERROR)
        result = self.op_bin_int[op_value](left.value, right.value)
        self.stack.append(Value(lookup.INTEGER, result))

    def __bin_op_cmp(self, op_value: int) -> None:
        right: Value = self.__pop()
        left: Value = self.__pop()
        result = self.op_bin_cmp[op_value](left.value, right.value)
        self.stack.append(Value(lookup.BOOLEAN, result))

    def __write(self, _=None) -> None:
        self.__check_stack_underflow()
        peek = self.stack[-1]
        wrapper_value = {
            lookup.INTEGER: peek.value,
            lookup.STRING: peek.value,
            lookup.NONE: "NONE",
            lookup.BOOLEAN: "TRUE" if peek.value == 1 else "FALSE"
        }
        if peek.value_type in wrapper_value:
            print(wrapper_value[peek.value_type])
            return
        print(f"<type({peek.value_type}): {peek.value}>")

    def __set_index(self, index: int) -> None:
        self.__check_stack_underflow()
        value: Value = self.stack.pop()
        list_data = self.stack[-1]
        if list_data.value_type not in { lookup.LIST, lookup.STRING }:
            raise Fault(FaultType.TYPE_ERROR)
        if -len(list_data.value) <= index < len(list_data.value):
            self.stack[-1].value[index] = value
        else:
            raise Fault(FaultType.INDEX_OUT_OF_BOUND)

    def __get_index(self, index: int) -> None:
        self.__check_stack_underflow()
        list_data = self.stack.pop()
        if list_data.value_type not in { lookup.LIST, lookup.STRING }:
            raise Fault(FaultType.TYPE_ERROR)
        if -len(list_data.value) <= index < len(list_data.value):
            self.stack.append(list_data.value[index])
        else:
            raise Fault(FaultType.INDEX_OUT_OF_BOUND)

    def __make_list(self, count: int) -> None:
        self.__check_stack_underflow(size=count-1)
        items = self.stack[-count::]
        self.stack = self.stack[:-count]
        self.stack.append(Value(
            value_type=lookup.LIST,
            value=items
        ))

    def __call(self, count: int) -> None:
        self.__check_stack_underflow()
        if len(self.stack) < count + 1:
            raise Fault(FaultType.STACK_UNDERFLOW)
        if self.stack[-count-1].value_type != lookup.FUNCTION:
            raise Fault(FaultType.OUT_OF_ORDER)
        self.__load_function(count)

    def __ret(self, _=None) -> None:
        frame: Frame = self.__get_current_frame()
        self.__gc(frame.func)
        return_value = self.__pop()
        self.stack = self.stack[:frame.base_pointer - 1]
        self.stack.append(return_value)
        self.frames.pop()

    def __call_native_function(self, function: Function, args_count: int) -> None:
        args: list[Value] = self.stack[-args_count:] if args_count > 0 else list()
        self.stack = self.stack[:-args_count-1][::-1]
        return_value = function.native_pointer(args)
        if type(return_value) != Value:
            raise Fault(FaultType.NATIVE_FUNCTION_RETURN)
        self.stack.append(return_value)

    def __jump(self, instruction_pointer: int) -> None:
        frame = self.__get_current_frame()
        frame.ip = instruction_pointer - 1

    def __jump_if_false(self, instruction_pointer: int) -> None:
        frame = self.__get_current_frame()
        value: Value = self.__pop()
        if value.value_type != lookup.BOOLEAN:
            raise Fault(FaultType.TYPE_ERROR)
        if value.value == 0:
            frame.ip = instruction_pointer - 1

    def __dup(self, _=None) -> None:
        value: Value = self.__pop()
        self.stack.append(value)
        self.stack.append(value)

    def __store(self, pointer: int) -> None:
        frame = self.__get_current_frame()
        mem_base_pointer = frame.mem_base_pointer
        if mem_base_pointer + pointer >= len(self.memory):
            raise Fault(FaultType.INVALID_LOCAL_SLOT)
        self.memory[mem_base_pointer + pointer] = self.__pop()

    def __load(self, pointer: int) -> None:
        frame = self.__get_current_frame()
        mem_base_pointer = frame.mem_base_pointer
        if mem_base_pointer + pointer >= len(self.memory):
            raise Fault(FaultType.INVALID_LOCAL_SLOT)
        self.stack.append(self.memory[mem_base_pointer + pointer])

    def __gc(self, frame: Function) -> None:
        local_count = frame.local_count
        if local_count == 0: return
        if len(self.memory) + local_count < 0:
            raise Fault(FaultType.GC_FAILURE)
        self.memory = self.memory[:-frame.local_count]

    def __check_stack_underflow(self, size: int=0):
        frame = self.__get_current_frame()
        if len(self.stack) - size <= frame.base_pointer:
            raise Fault(FaultType.STACK_UNDERFLOW)

class Frame:
    def __init__(self, func: Function, base_pointer: int, mem_base_pointer: int):
        self.func = func
        self.ip = 0
        self.base_pointer = base_pointer
        self.mem_base_pointer = mem_base_pointer
