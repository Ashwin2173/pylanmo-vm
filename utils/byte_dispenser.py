class ByteDispenser:
    def __init__(self, bytecode: bytes):
        self.bytecode = bytecode
        self.pointer = 0

    def next_int(self, size: int) -> int:
         return int.from_bytes(self.next(size), byteorder='little')

    def next_str(self, size: int) -> str:
        return self.next(size).decode("utf-8")

    def next(self, size: int) -> bytes:
        start_pointer = self.pointer
        self.pointer += size
        return self.bytecode[start_pointer: self.pointer]