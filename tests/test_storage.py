from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext, InvalidStorageSlot, InvalidStorageValue
from smol_evm.opcodes import SLOAD
from shared import with_stack_contents

import pytest

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_invalid_slot_negative(context):
    with pytest.raises(InvalidStorageSlot) as excinfo:
        context.storage.get(-1)
    assert excinfo.value.args[0] == -1


def test_invalid_slot_too_big(context):
    with pytest.raises(InvalidStorageSlot) as excinfo:
        context.storage.put(MAX_UINT256 + 1, 0)
    assert excinfo.value.args[0] == MAX_UINT256 + 1


def test_invalid_value_negative(context):
    with pytest.raises(InvalidStorageValue) as excinfo:
        context.storage.put(0, -1)
    assert excinfo.value.args[0] == -1


def test_invalid_value_too_big(context):
    with pytest.raises(InvalidStorageValue) as excinfo:
        context.storage.put(0, MAX_UINT256 + 1)
    assert excinfo.value.args[0] == MAX_UINT256 + 1


def test_simple_sload_uninitialised(context):
    # reading uninitialised storage slot 0
    SLOAD.execute(with_stack_contents(context, (0,)))
    assert context.stack.pop() == 0


def test_simple_sload_preinitialized(context):
    context.storage.put(1, 42)
    SLOAD.execute(with_stack_contents(context, (1,)))
    assert context.stack.pop() == 42

