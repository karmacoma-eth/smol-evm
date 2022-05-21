from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import DUP1, DUP2
from smol_evm.stack import Stack, StackOverflow, StackUnderflow, InvalidStackItem

from shared import with_stack_contents

import pytest

@pytest.fixture
def stack() -> Stack:
    return Stack()

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()

def test_underflow_pop(stack):
    with pytest.raises(StackUnderflow):
        stack.pop()

def test_underflow_empty_peek(stack):
    with pytest.raises(StackUnderflow):
        stack.peek(0)

def test_underflow_non_empty_peek(stack):
    stack.push(1)
    stack.push(2)

    with pytest.raises(StackUnderflow):
        stack.peek(2)

def test_happy_peek(stack):
    stack.push(1)
    stack.push(2)
    assert stack.peek(0) == 2
    assert stack.peek(1) == 1


def test_overflow():
    stack = Stack(max_depth=1)

    stack.push(0)
    with pytest.raises(StackOverflow):
        stack.push(1)

def test_push_pop(stack):
    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2
    assert stack.pop() == 1


def test_push_uint256_max(stack):
    stack.push(MAX_UINT256)
    assert stack.pop() == MAX_UINT256


def test_invalid_value_negative(stack):
    with pytest.raises(InvalidStackItem) as excinfo:
        stack.push(-1)
    assert excinfo.value.args[0]['item'] == -1


def test_invalid_value_too_big(stack):
    with pytest.raises(InvalidStackItem) as excinfo:
        stack.push(MAX_UINT256 + 1)
    assert excinfo.value.args[0]['item'] == MAX_UINT256 + 1

def test_swap1(stack):
    for x in [1, 2, 3]:
        stack.push(x)
    stack.swap(1)
    assert stack.pop() == 2
    assert stack.pop() == 3
    assert stack.pop() == 1

def test_swap2(stack):
    for x in [1, 2, 3]:
        stack.push(x)
    stack.swap(2)
    assert stack.pop() == 1
    assert stack.pop() == 2
    assert stack.pop() == 3

def test_swap_underflow(stack):
    with pytest.raises(StackUnderflow):
        stack.swap(1)

def test_peek(stack):
    for x in [1, 2, 3]:
        stack.push(x)
    assert stack.peek(0) == 3
    assert stack.peek(1) == 2
    assert stack.peek(2) == 1

def test_peek_underflow(stack):
    with pytest.raises(StackUnderflow):
        stack.peek(1)

def test_dup1(context):
    DUP1.execute(with_stack_contents(context, [1, 2, 3]))
    assert context.stack.pop() == 3
    assert context.stack.pop() == 3
    assert context.stack.pop() == 2

def test_dup2(context):
    DUP2.execute(with_stack_contents(context, [1, 2, 3]))
    assert context.stack.pop() == 2
    assert context.stack.pop() == 3
    assert context.stack.pop() == 2

