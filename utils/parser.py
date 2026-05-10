from typing import Callable

import utils.lookup as lookup

from utils.byte_dispenser import ByteDispenser

class Value:
    def __init__(self, value_type: int, value: any):
        self.value_type = value_type
        self.value = value

    def __repr__(self):
        return f"<{self.value_type}: {self.value}>"

class OpCode:
    def __init__(self, op_code: int, data: int):
        self.op_code = op_code
        self.data = data

class Function:
    def __init__(self, name: str, local_count: int, body: list[OpCode] | None, native_pointer: Callable | None, is_native: bool):
        self.name = name
        self.local_count = local_count
        self.body = body
        self.native_pointer = native_pointer
        self.is_native = is_native

    def __repr__(self):
        name = "native_function" if self.is_native else "custom_function"
        return f"<{name}: {self.name}>"

class Parser:
    def __init__(self, bd: ByteDispenser):
        self.bd = bd
        self.function_table = dict[str, Function]()
        self.symbol_table   = list[Value]()

        self.__load_native_function()
        self.__read_symbols()
        self.__read_functions()

    def __load_native_function(self) -> None:
        from utils.native_functions import get_all_native
        for name, func_pointer in get_all_native().items():
            self.function_table[name] = Function(
                name='print',
                local_count=0,
                body=None,
                native_pointer=func_pointer,
                is_native=True
            )

    def __read_symbols(self) -> None:
        symbol_count = self.bd.next_int(2)
        for _ in range(symbol_count):
            symbol_format = self.bd.next_int(1)
            if symbol_format == lookup.INTEGER:
                size = self.bd.next_int(4)
                int_value = self.bd.next_int(size)
                self.symbol_table.append(Value(lookup.INTEGER, int_value))
            elif symbol_format == lookup.STRING:
                size = self.bd.next_int(4)
                str_value = self.bd.next_str(size)
                self.symbol_table.append(Value(lookup.STRING, str_value))
            elif symbol_format == lookup.IDENTIFIER:
                size = self.bd.next_int(4)
                identifier = self.bd.next_str(size)
                self.symbol_table.append(Value(lookup.IDENTIFIER, identifier))
            elif symbol_format == lookup.FUNCTION:
                size = self.bd.next_int(4)
                function_name = self.bd.next_str(size)
                self.symbol_table.append(Value(lookup.FUNCTION, function_name))
            elif symbol_format == lookup.NONE:
                self.symbol_table.append(Value(lookup.NONE, None))
            elif symbol_format == lookup.BOOLEAN:
                value = self.bd.next_int(1)
                self.symbol_table.append(Value(lookup.BOOLEAN, value))
            else:
                assert False, f"Unhandled DataType: { str(symbol_format) }"

    def __read_functions(self) -> None:
        function_count = self.bd.next_int(2)
        for _ in range(function_count):
            function_name = self.symbol_table[self.bd.next_int(2)]
            local_count = self.bd.next_int(4)
            _ = self.bd.next_int(2)
            function_body = self.__read_function_body()
            self.function_table[function_name.value] = Function(
                name = function_name.value,
                local_count = local_count,
                body = function_body,
                native_pointer=None,
                is_native=False
            )

    def __read_function_body(self) -> list[OpCode]:
        function_body: list[OpCode] = list()
        op_code_count = self.bd.next_int(4)
        for _ in range(op_code_count):
            op_code = self.bd.next_int(1)
            data    = self.bd.next_int(2)
            function_body.append(OpCode(op_code = op_code, data = data))
        return function_body


