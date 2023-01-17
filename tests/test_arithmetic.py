from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import *

import pytest

from shared import with_stack


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_add_simple(context):
    ADD(with_stack(context, [1, 2]))
    assert context.stack.pop() == 3


def test_add_overflow(context):
    ADD(with_stack(context, [1, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_add_overflow2(context):
    ADD(with_stack(context, [3, MAX_UINT256 - 1]))
    assert context.stack.pop() == 1


def test_sub_simple(context):
    SUB(with_stack(context, [2, 3]))
    assert context.stack.pop() == 1


def test_sub_underflow(context):
    SUB(with_stack(context, [2, 1]))
    assert context.stack.pop() == MAX_UINT256


def test_sub_EXTREME(context):
    SUB(with_stack(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_div_simple(context):
    DIV(with_stack(context, [2, 10]))
    assert context.stack.pop() == 5


def test_div_floor(context):
    DIV(with_stack(context, [2, 11]))
    assert context.stack.pop() == 5


def test_div_EXTREME(context):
    DIV(with_stack(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 1


def test_div_zero(context):
    DIV(with_stack(context, [MAX_UINT256, 0]))
    assert context.stack.pop() == 0


def test_div_by_zero(context):
    DIV(with_stack(context, [0, 1]))
    assert context.stack.pop() == 0


def test_sdiv_simple(context):
    # NOTE: int(MAX_UINT256) is -1
    # 20 / -2
    SDIV(with_stack(context, [int_to_uint(-2), 20]))
    assert context.stack.pop() == int_to_uint(-10)


def test_sdiv_floor(context):
    # -11 / -2
    SDIV(with_stack(context, [int_to_uint(-2), int_to_uint(-11)]))
    assert context.stack.pop() == 5


def test_sdiv_EXTREME(context):
    # -1 / 1
    SDIV(with_stack(context, [1, MAX_UINT256]))
    assert context.stack.pop() == int_to_uint(-1)


def test_sdiv_zero(context):
    # 0 / -1
    SDIV(with_stack(context, [MAX_UINT256, 0]))
    assert context.stack.pop() == 0


def test_sdiv_by_zero(context):
    # -1 / 0
    SDIV(with_stack(context, [0, int_to_uint(-11)]))
    assert context.stack.pop() == 0


def test_mod_simple(context):
    MOD(with_stack(context, [2, 11]))
    assert context.stack.pop() == 1


def test_mod_zero(context):
    # 0 mod 11
    MOD(with_stack(context, [11, 0]))
    assert context.stack.pop() == 0


def test_mod_by_zero(context):
    # 1 mod 0
    MOD(with_stack(context, [0, 1]))
    assert context.stack.pop() == 0


def test_mod_EXTREME(context):
    MOD(with_stack(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_smod_simple(context):
    # 11 % -2
    SMOD(with_stack(context, [int_to_uint(-2), 11]))
    assert context.stack.pop() == int_to_uint(-1)


def test_smod_zero(context):
    # 0 % -11
    SMOD(with_stack(context, [int_to_uint(-11), 0]))
    assert context.stack.pop() == 0


def test_smod_by_zero(context):
    # -1 % 0
    SMOD(with_stack(context, [0, int_to_uint(-1)]))
    assert context.stack.pop() == 0


def test_smod_EXTREME(context):
    # -1 % -1 == 0
    SMOD(with_stack(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_addmod_simple(context):
    ADDMOD(with_stack(context, [2, 4, 3]))
    assert context.stack.pop() == 1


def test_mulmod_simple(context):
    MULMOD(with_stack(context, [2, 4, 3]))
    assert context.stack.pop() == 0


def test_exp_simple(context):
    EXP(with_stack(context, [2, 10]))
    assert context.stack.pop() == 100


def test_exp_overflow(context):
    EXP(with_stack(context, [2, MAX_UINT256 - 1]))
    assert context.stack.pop() < MAX_UINT256


def test_signextend_simple(context):
    SIGNEXTEND(with_stack(context, [0xFF, 0]))
    assert context.stack.pop() == MAX_UINT256

    SIGNEXTEND(with_stack(context, [0x7F, 0]))
    assert context.stack.pop() == 0x7F

    SIGNEXTEND(with_stack(context, [0xABCD, 1]))
    assert context.stack.pop() == 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFABCD

    SIGNEXTEND(with_stack(context, [0x1234, 1]))
    assert context.stack.pop() == 0x1234


def test_signextend_EXTREME(context):
    SIGNEXTEND(with_stack(context, [0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFAABB, 100]))
    assert context.stack.pop() == 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFAABB


def test_sar_signed_normal(context):
    SAR(with_stack(context, [int_to_uint(-4), 2]))
    assert context.stack.pop() == int_to_uint(-1)


def test_sar_signed_big(context):
    SAR(with_stack(context, [0x8000000000000000000000000000000000000000000000000000000000000000, 1]))
    assert context.stack.pop() == 0xC000000000000000000000000000000000000000000000000000000000000000


def test_sar_massive_shift(context):
    SAR(with_stack(context, [int_to_uint(-256), 0xFFFFFFFF]))
    assert context.stack.pop() == int_to_uint(-1)


def test_sar_unsigned_normal(context):
    SAR(with_stack(context, [4, 1]))
    assert context.stack.pop() == 2


def test_sar_unsigned_big(context):
    SAR(with_stack(context, [0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 1]))
    assert context.stack.pop() == 0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


def test_sar_by_zero(context):
    SAR(with_stack(context, [1, 0]))
    assert context.stack.pop() == 1
