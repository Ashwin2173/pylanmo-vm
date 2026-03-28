# look up v1.0

INTEGER = 1
STRING = 2
IDENTIFIER = 3
FUNCTION = 4

OP_PUSH = 1
OP_POP = 2
OP_ADD = 3
OP_PEEK = 4
OP_CALL = 5
OP_HALT = 6
OP_RET = 7

from enum import Enum, auto

class FaultType(Enum):
    STACK_UNDERFLOW = auto()
    NO_FRAME = auto()
    TYPE_ERROR = auto()
    UNDEFINED_FUNCTION = auto()

    OUT_OF_ORDER = auto()
    NO_RET = auto()

    DONE = auto()