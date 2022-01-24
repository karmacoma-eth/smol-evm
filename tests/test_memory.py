from yolo_evm.memory import Memory, InvalidMemoryAccess, InvalidMemoryValue

import pytest

@pytest.fixture
def memory() -> Memory:
    return Memory()

def test_invalid_offset(memory):
    with pytest.raises(InvalidMemoryAccess) as excinfo:
        memory.store(-1, 1)
    assert excinfo.value.args[0]['offset'] == -1


def test_store_far_offset(memory):
    memory.store(100, 42)
    for i in range(0, 100):
        assert memory.load(i) == 0
    assert memory.load(100) == 42


def test_store_max(memory):
    max_value = 2 ** 8 - 1
    memory.store(0, max_value)
    assert memory.load(0) == max_value


def test_invalid_value_negative(memory):
    with pytest.raises(InvalidMemoryValue) as excinfo:
        memory.store(1, -1)
    assert excinfo.value.args[0]['value'] == -1


def test_invalid_value_too_big(memory):
    with pytest.raises(InvalidMemoryValue) as excinfo:
        memory.store(1, 1 << 257)
    assert excinfo.value.args[0]['value'] == 1 << 257