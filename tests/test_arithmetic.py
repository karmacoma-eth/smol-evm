from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import (
    ADD,
    ADDMOD,
    DIV,
    SDIV,
    EXP,
    MOD,
    SMOD,
    MULMOD,
    SIGNEXTEND,
    SUB,
    int_to_uint,
)

import pytest

from shared import with_stack_contents


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_add_simple(context):
    ADD.execute(with_stack_contents(context, [1, 2]))
    assert context.stack.pop() == 3


def test_add_overflow(context):
    ADD.execute(with_stack_contents(context, [1, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_add_overflow2(context):
    ADD.execute(with_stack_contents(context, [3, MAX_UINT256 - 1]))
    assert context.stack.pop() == 1


def test_sub_simple(context):
    SUB.execute(with_stack_contents(context, [2, 3]))
    assert context.stack.pop() == 1


def test_sub_underflow(context):
    SUB.execute(with_stack_contents(context, [2, 1]))
    assert context.stack.pop() == MAX_UINT256


def test_sub_EXTREME(context):
    SUB.execute(with_stack_contents(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_div_simple(context):
    DIV.execute(with_stack_contents(context, [2, 10]))
    assert context.stack.pop() == 5


def test_div_floor(context):
    DIV.execute(with_stack_contents(context, [2, 11]))
    assert context.stack.pop() == 5


def test_div_EXTREME(context):
    DIV.execute(with_stack_contents(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 1


def test_div_zero(context):
    DIV.execute(with_stack_contents(context, [MAX_UINT256, 0]))
    assert context.stack.pop() == 0


def test_div_by_zero(context):
    DIV.execute(with_stack_contents(context, [0, 1]))
    assert context.stack.pop() == 0


def test_sdiv_simple(context):
    # NOTE: int(MAX_UINT256) is -1
    # 20 / -2
    SDIV.execute(with_stack_contents(context, [int_to_uint(-2), 20]))
    assert context.stack.pop() == int_to_uint(-10)


def test_sdiv_floor(context):
    # -11 / -2
    SDIV.execute(with_stack_contents(context, [int_to_uint(-2), int_to_uint(-11)]))
    assert context.stack.pop() == 5


def test_sdiv_EXTREME(context):
    # -1 / 1
    SDIV.execute(with_stack_contents(context, [1, MAX_UINT256]))
    assert context.stack.pop() == int_to_uint(-1)


def test_sdiv_zero(context):
    # 0 / -1
    SDIV.execute(with_stack_contents(context, [MAX_UINT256, 0]))
    assert context.stack.pop() == 0


def test_mod_simple(context):
    MOD.execute(with_stack_contents(context, [2, 11]))
    assert context.stack.pop() == 1


def test_mod_zero(context):
    MOD.execute(with_stack_contents(context, [11, 0]))
    assert context.stack.pop() == 0


def test_mod_EXTREME(context):
    MOD.execute(with_stack_contents(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_smod_simple(context):
    # 11 % -2
    SMOD.execute(with_stack_contents(context, [int_to_uint(-2), 11]))
    assert context.stack.pop() == int_to_uint(-1)


def test_smod_zero(context):
    SMOD.execute(with_stack_contents(context, [int_to_uint(-11), 0]))
    assert context.stack.pop() == 0


def test_smod_EXTREME(context):
    # -1 % -1 == 0
    SMOD.execute(with_stack_contents(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 0


def test_addmod_simple(context):
    ADDMOD.execute(with_stack_contents(context, [2, 4, 3]))
    assert context.stack.pop() == 1


def test_mulmod_simple(context):
    MULMOD.execute(with_stack_contents(context, [2, 4, 3]))
    assert context.stack.pop() == 0


def test_exp_simple(context):
    EXP.execute(with_stack_contents(context, [2, 10]))
    assert context.stack.pop() == 100


def test_exp_overflow(context):
    EXP.execute(with_stack_contents(context, [2, MAX_UINT256 - 1]))
    assert context.stack.pop() < MAX_UINT256

def test_SIGNEXTEND_simple(context):
    SIGNEXTEND.execute(with_stack_contents(context, [0xFF, 0]))
    assert context.stack.pop() == MAX_UINT256

    SIGNEXTEND.execute(with_stack_contents(context, [0x7F, 0]))
    assert context.stack.pop() == 0x7F

    SIGNEXTEND.execute(with_stack_contents(context, [0xABCD, 1]))
    assert context.stack.pop() == 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffabcd

    SIGNEXTEND.execute(with_stack_contents(context, [0x1234, 1]))
    assert context.stack.pop() == 0x1234

def test_SIGNEXTEND_EXTREME(context):
    SIGNEXTEND.execute(with_stack_contents(context, [0x1fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffaabb, 100]))
    assert context.stack.pop() == 0x1fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffaabb
