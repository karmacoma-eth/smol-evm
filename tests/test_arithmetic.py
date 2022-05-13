from yolo_evm.constants import MAX_UINT256
from yolo_evm.context import ExecutionContext
from yolo_evm.opcodes import ADD

import pytest

from shared import with_stack_contents

@pytest.fixture
def context() -> ExecutionContext:
    code = bytes(ADD.opcode)
    return ExecutionContext(code=code)

def test_simple(context):
    ADD.execute(with_stack_contents(context, [1, 2]))
    assert context.stack.pop() == 3

def test_overflow(context):
    ADD.execute(with_stack_contents(context, [1, MAX_UINT256]))
    assert context.stack.pop() == 0

def test_overflow(context):
    ADD.execute(with_stack_contents(context, [3, MAX_UINT256 - 1]))
    assert context.stack.pop() == 1

