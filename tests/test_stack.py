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
    stack.push(2 ** 256 - 1)
    assert stack.pop() == 2 ** 256 - 1


def test_invalid_value_negative(stack):
    with pytest.raises(InvalidStackItem) as excinfo:
        stack.push(-1)
    assert excinfo.value.args[0]['item'] == -1


def test_invalid_value_too_big(stack):
    with pytest.raises(InvalidStackItem) as excinfo:
        stack.push(1 << 257)
    assert excinfo.value.args[0]['item'] == 1 << 257