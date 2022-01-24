from yolo_evm.stack import Stack, StackOverflow, StackUnderflow, InvalidStackItem

import pytest

@pytest.fixture
def stack() -> Stack:
    return Stack()

def test_underflow(stack):
    with pytest.raises(StackUnderflow) as e:
        stack.pop()

def test_overflow():
    stack = Stack(max_depth=1)

    stack.push(0)
    with pytest.raises(StackOverflow) as e:
        stack.push(1)

def test_push_pop(stack):
    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2
    assert stack.pop() == 1

def test_invalid_value(stack):
    with pytest.raises(InvalidStackItem):
        stack.push(-1)

    with pytest.raises(InvalidStackItem):
        stack.push(1 << 257)