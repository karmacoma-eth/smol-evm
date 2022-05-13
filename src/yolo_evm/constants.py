MAX_UINT256 = 2 ** 256 - 1
MAX_UINT8 = 2 ** 8 - 1
MAX_STACK_DEPTH = 1024

def is_valid_uint256(value: int) -> bool:
    return 0 <= value <= MAX_UINT256

def is_valid_uint8(value: int) -> bool:
    return 0 <= value <= MAX_UINT8
