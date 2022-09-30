from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import AND,OR,XOR,NOT,SHR

import pytest

from shared import with_stack_contents

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()

def test_or_simple(context):
    OR.execute(with_stack_contents(context,[int("0x1F",16),int("0xF0",16)]))
    assert context.stack.pop() == int("0xFF",16)

def test_and_simple(context):
    AND.execute(with_stack_contents(context,[int("0x1F",16),int("0xF0",16)]))
    assert context.stack.pop() == int("0x10",16)

def test_xor_simple(context):
    XOR.execute(with_stack_contents(context,[int("0x1F",16),int("0xF0",16)]))
    assert context.stack.pop() == int("0xEF",16)

def test_not_simple(context):
    NOT.execute(with_stack_contents(context, [1]))
    assert context.stack.pop() == int("0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe",16)

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
