from enum import Enum
from numpy import dtype

class AthenaDataTypes(Enum):
    int = dtype('int64')
    float = dtype('float64')
    string = dtype('O')