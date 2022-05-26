from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import LT

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
