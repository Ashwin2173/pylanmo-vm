import sys

from utils.byte_dispenser import ByteDispenser
from utils.exceptions import Fault
from utils.lookup import FaultType
from utils.parser import Parser
from utils.vm import VM

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
    vm = VM(parser.symbol_table, parser.function_table)
    try:
        vm.load_main()
        while True:
            vm.step_in()
            print(vm.memory)
    except Fault as f:
        if f.fault_code != FaultType.DONE:
            func_name = "~"
            func_ip = "~"
            if len(vm.frames) > 0:
                func_name = vm.frames[-1].func.name
                func_ip = vm.frames[-1].ip
            print(f"VM FAULT[{func_name}:~{func_ip}]: {f.fault_code}")
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"VM CORE FAULT: {e}")
        sys.exit(1)

def fault(message: str, exit_code: int=1):
    print(f"ERROR: {message}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main(sys.argv)