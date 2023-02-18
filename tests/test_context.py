from smol_evm.opcodes import *


def test_decode_truncated_push_arg():
    """can we decode a PUSH instruction with a truncated arg?"""

    code = assemble([PUSH(0x4243)])
    context = ExecutionContext(code=code[:-1])
    assert decode_opcode(context) == PUSH(0x4200)
