from yolo_evm.constants import MAX_UINT256
from yolo_evm.context import ExecutionContext
from yolo_evm.opcodes import ADD, SUB

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
