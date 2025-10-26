from enum import Enum

class AresDataType(Enum):
    UNKNOWN = 0
    NULL = 1
    BOOLEAN = 2
    STRING = 3
    NUMBER = 4
    STRING_ARRAY = 5
    NUMBER_ARRAY = 6
    BYTE_ARRAY = 7
    BOOL_ARRAY = 8

class Outcome(Enum):
    UNSPECIFIED_OUTCOME = 0
    SUCCESS = 1
    FAILURE = 2
    WARNING = 3
    CANCELED = 4