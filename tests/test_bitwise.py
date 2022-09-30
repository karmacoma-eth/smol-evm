from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import SHR, SHL

import pytest

from shared import with_stack_contents

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()

def test_shr_simple(context):
    SHR.execute(with_stack_contents(context, [16, 1]))
    assert context.stack.pop() == 8

def test_shr_big(context):
    SHR.execute(with_stack_contents(context, [16, 5]))
    assert context.stack.pop() == 0

def test_shr_by_zero(context):
    SHR.execute(with_stack_contents(context, [16, 0]))
    assert context.stack.pop() == 16

def test_shr_non_power_of_two(context):
    SHR.execute(with_stack_contents(context, [15, 1]))
    assert context.stack.pop() == 7



def test_shl_non_power_of_two(context):
    SHL.execute(with_stack_contents(context, [15, 1]))
    assert context.stack.pop() == 30
