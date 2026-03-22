import utils.lookup as lookup

from utils.byte_dispenser import ByteDispenser

OP_WITH_LOOKUP = {
    lookup.PUSH
}

class OpCode:
    def __init__(self, op_code: int, data: any):
        self.op_code = op_code
        self.data = data

class Function:
    def __init__(self, name: str, arg_count: int, body: list[OpCode]):
        self.name = name
        self.arg_count = arg_count
        self.body = body

class Parser:
    def __init__(self, bd: ByteDispenser):
        self.bd = bd
        self.function_table = dict()
        self.symbol_table   = list()

        self.__read_symbols()
        self.__read_functions()

    def __read_symbols(self) -> None:
        symbol_count = self.bd.next_int(2)
        for _ in range(symbol_count):
            symbol_format = self.bd.next_int(1)
            if symbol_format == lookup.INTEGER:
                size = self.bd.next_int(4)
                self.symbol_table.append(self.bd.next_int(size))
            elif symbol_format == lookup.STRING:
                size = self.bd.next_int(4)
                self.symbol_table.append(self.bd.next_str(size))
            elif symbol_format == lookup.IDENTIFIER:
                size = self.bd.next_int(4)
                self.symbol_table.append(self.bd.next_str(size))
            else:
                assert False, f"Unhandled DataType: { str(symbol_format) }"

    def __read_functions(self) -> None:
        function_count = self.bd.next_int(2)
        for _ in range(function_count):
            function_name = self.symbol_table[self.bd.next_int(2)]
            function_args = self.bd.next_int(1)
            _ = self.bd.next_int(4)
            _ = self.bd.next_int(2)
            function_body = self.__read_function_body()
            function_lookup_name = f"{function_name}{function_args}"
            self.function_table[function_lookup_name] = Function(
                name = function_name,
                arg_count = function_args,
                body = function_body
            )

    def __read_function_body(self) -> list[OpCode]:
        function_body: list[OpCode] = list()
        op_code_count = self.bd.next_int(4)
        for _ in range(op_code_count):
            op_code = self.bd.next_int(1)
            data    = self.bd.next_int(2)
            if op_code in OP_WITH_LOOKUP:
                data = self.symbol_table[data]
            function_body.append(OpCode(op_code = op_code, data = data))
        return function_body

