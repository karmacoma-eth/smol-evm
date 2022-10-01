from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import LT, GT, SLT, SGT, EQ, ISZERO, uint_to_int, int_to_uint

import pytest

from shared import with_stack_contents

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()

def test_lt_equal(context):
    LT.execute(with_stack_contents(context, [1, 1]))
    assert context.stack.pop() == 0

def test_lt_simple(context):
    LT.execute(with_stack_contents(context, [1, 0]))
    assert context.stack.pop() == 1

def test_gt_equal(context):
    GT.execute(with_stack_contents(context, [1, 1]))
    assert context.stack.pop() == 0

def test_gt_simple(context):
    GT.execute(with_stack_contents(context, [0, 1]))
    assert context.stack.pop() == 1

def test_slt_equal(context):
    SLT.execute(with_stack_contents(context, [int_to_uint(-1), int_to_uint(-1)]))
    assert context.stack.pop() == 0

def test_slt_simple(context):
    SLT.execute(with_stack_contents(context, [10, int_to_uint(-1)]))
    assert context.stack.pop() == 1

def test_slt_extreme(context):
    # MAX_UINT256 is -1
    SLT.execute(with_stack_contents(context, [10, MAX_UINT256]))
    assert context.stack.pop() == 1

def test_sgt_equal(context):
    SGT.execute(with_stack_contents(context, [1, 1]))
    assert context.stack.pop() == 0

def test_sgt_simple(context):
    SGT.execute(with_stack_contents(context, [int_to_uint(-5), 10]))
    assert context.stack.pop() == 1

def test_sgt_extreme(context):
    # MAX_UINT256 is -1
    SGT.execute(with_stack_contents(context, [MAX_UINT256, 10]))
    assert context.stack.pop() == 1

def test_eq_simple(context):
    EQ.execute(with_stack_contents(context, [1, 1]))
    assert context.stack.pop() == 1

def test_eq_big(context):
    EQ.execute(with_stack_contents(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 1

def test_eq_zero(context):
    EQ.execute(with_stack_contents(context, [0, 0]))
    assert context.stack.pop() == 1

def test_eq_not_equal(context):
    EQ.execute(with_stack_contents(context, [1, 0]))
    assert context.stack.pop() == 0

def test_iszero_zero(context):
    ISZERO.execute(with_stack_contents(context, [1, 0]))
    assert context.stack.pop() == 1

def test_iszero_notzero(context):
    ISZERO.execute(with_stack_contents(context, [0, 1]))
    assert context.stack.pop() == 0
