from smol_evm.constants import MAX_UINT256, HALF_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import LT, GT, EQ, ISZERO, SLT, SGT

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

def test_slt_equal_zero(context):
    SLT.execute(with_stack_contents(context, [0, 0]))
    assert context.stack.pop() == 0

def test_slt_equal_pos(context):
    SLT.execute(with_stack_contents(context, [1, 1]))
    assert context.stack.pop() == 0

def test_slt_equal_neg(context):
    SLT.execute(with_stack_contents(context, [HALF_UINT256, HALF_UINT256]))
    assert context.stack.pop() == 0

def test_slt_true_pos_pos(context):
    SLT.execute(with_stack_contents(context, [1, 0]))
    assert context.stack.pop() == 1

def test_slt_true_neg_pos(context):
    SLT.execute(with_stack_contents(context, [1, HALF_UINT256]))
    assert context.stack.pop() == 1

def test_slt_true_neg_neg(context):
    SLT.execute(with_stack_contents(context, [HALF_UINT256 + 1, HALF_UINT256]))
    assert context.stack.pop() == 1

def test_slt_false_pos_pos(context):
    SLT.execute(with_stack_contents(context, [0, 1]))
    assert context.stack.pop() == 0

def test_slt_false_neg_pos(context):
    SLT.execute(with_stack_contents(context, [HALF_UINT256, 1]))
    assert context.stack.pop() == 0

def test_slt_false_neg_neg(context):
    SLT.execute(with_stack_contents(context, [HALF_UINT256, HALF_UINT256 + 1]))
    assert context.stack.pop() == 0

def test_sgt_equal_zero(context):
    SGT.execute(with_stack_contents(context, [0, 0]))
    assert context.stack.pop() == 0

def test_sgt_equal_pos(context):
    SGT.execute(with_stack_contents(context, [1, 1]))
    assert context.stack.pop() == 0

def test_sgt_equal_neg(context):
    SGT.execute(with_stack_contents(context, [HALF_UINT256, HALF_UINT256]))
    assert context.stack.pop() == 0

def test_sgt_true_pos_pos(context):
    SGT.execute(with_stack_contents(context, [0, 1]))
    assert context.stack.pop() == 1

def test_sgt_true_neg_pos(context):
    SGT.execute(with_stack_contents(context, [HALF_UINT256, 1]))
    assert context.stack.pop() == 1

def test_sgt_true_neg_neg(context):
    SGT.execute(with_stack_contents(context, [HALF_UINT256, HALF_UINT256 + 1]))
    assert context.stack.pop() == 1

def test_sgt_false_pos_pos(context):
    SGT.execute(with_stack_contents(context, [1, 0]))
    assert context.stack.pop() == 0

def test_sgt_false_neg_pos(context):
    SGT.execute(with_stack_contents(context, [1, HALF_UINT256]))
    assert context.stack.pop() == 0

def test_sgt_false_neg_neg(context):
    SGT.execute(with_stack_contents(context, [HALF_UINT256 + 1, HALF_UINT256]))
    assert context.stack.pop() == 0
