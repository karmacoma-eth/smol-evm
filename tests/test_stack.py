from yolo_evm.constants import MAX_UINT256
from yolo_evm.stack import Stack, StackOverflow, StackUnderflow, InvalidStackItem

import pytest

@pytest.fixture
def stack() -> Stack:
    return Stack()

def test_underflow(stack):
    with pytest.raises(StackUnderflow):
        stack.pop()

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

