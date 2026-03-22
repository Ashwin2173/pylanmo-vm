import sys

from utils.byte_dispenser import ByteDispenser
from utils.parser import Parser

MAGIC = 2273
MAJOR_VERSION = 1
MINOR_VERSION = 0

def open_program(args: list[str]) -> tuple[bytes, str] | None:
    for arg in args:
        if arg.endswith(".lmc"):
            with open(arg, 'rb') as program_file:
                return program_file.read(), arg
    fault("Required .lmc file")

def main(args: list[str]) -> None:
    program, path = open_program(args)
    bd = ByteDispenser(program)
    magic = bd.next_int(4)
    major_version = bd.next_int(2)
    minor_version = bd.next_int(2)
    if magic != MAGIC:
        fault("Invalid bytecode format")
    if major_version != MAJOR_VERSION or minor_version != MINOR_VERSION:
        fault(f"Version v{major_version}.{minor_version} is not supported")
    parser = Parser(bd)
    print(parser)

def fault(message: str, exit_code: int=1):
    print(f"ERROR: {message}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main(sys.argv)