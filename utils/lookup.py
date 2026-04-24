# look up v1.0

INTEGER = 1
STRING = 2
IDENTIFIER = 3
FUNCTION = 4
NONE = 5
BOOLEAN = 6

OP_PUSH = 1
OP_POP = 2
OP_BIN = 3
OP_WRITE = 4
OP_CALL = 5
OP_HALT = 6
OP_RET = 7
OP_JUMP = 8
OP_JUMP_IF_FALSE = 9
OP_DUP = 10
OP_STORE = 11
OP_LOAD = 12

BIN_OP_ADD = 1
BIN_OP_SUB = 2
BIN_OP_MUL = 3
BIN_OP_DIV = 4
BIN_OP_MOD = 5

BIN_OP_EEQ = 6
BIN_OP_NEQ = 7
BIN_OP_GEQ = 8
BIN_OP_GTN = 9
BIN_OP_LEQ = 10
BIN_OP_LTN = 11

BIN_OP_AND = 12
BIN_OP_OR  = 13

from enum import Enum, auto

class FaultType(Enum):
    STACK_UNDERFLOW = auto()
    NO_FRAME = auto()
    TYPE_ERROR = auto()
    UNDEFINED_FUNCTION = auto()
    INVALID_BIN_OP = auto()

    OUT_OF_ORDER = auto()
    INVALID_LOCAL_SLOT = auto()
    GC_FAILURE = auto()
    NO_RET = auto()

    DONE = auto()