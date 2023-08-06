from enum import Enum


class ReturnType(str, Enum):
    LIST = "list"
    DICT = "dict"
    NUMBA_DICT = "numba_dict"
    NUMBA_LIST = "numba_list"
    NUMPY_ARRAY = "ndarray"
