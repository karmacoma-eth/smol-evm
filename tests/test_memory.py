from smol_evm.opcodes import assemble, PUSH1, RETURN, MLOAD, MSTORE8, MSIZE
from smol_evm.memory import Memory, InvalidMemoryAccess, InvalidMemoryValue
from smol_evm.runner import run

import pytest

@pytest.fixture
def memory() -> Memory:
    return Memory()

def store0(memory, offset):
    memory.store(offset, 0)

def test_invalid_offset(memory):
    with pytest.raises(InvalidMemoryAccess) as excinfo:
        memory.store(-1, 1)
    assert excinfo.value.args[0]['offset'] == -1


def test_store_far_offset(memory):
    memory.store(100, 42)
    for i in range(0, 100):
        assert memory.load(i) == 0
    assert memory.load(100) == 42


def test_memory_increments_by_word():
    for op in [store0, Memory.load]:
        memory = Memory()

        # all fit in the same word
        op(memory, 0)
        assert len(memory) == 32
        assert memory.active_words() == 1

        op(memory, 1)
        assert memory.active_words() == 1

        op(memory, 31)
        assert memory.active_words() == 1

        # activate a second word
        op(memory, 32)
        assert memory.active_words() == 2

        # go far
        op(memory, 100)
        assert memory.active_words() == 4


def test_load_range_increments_by_word(memory):
    # when we only read the first word, there is no expansion beyond that
    memory.load_range(0, 32)
    assert memory.active_words() == 1

    # when we read across two words, then we expand
    memory.load_range(1, 32)
    assert memory.active_words() == 2

    # when we read much further, we expand by multiple words
    memory.load_range(68, 32)
    assert memory.active_words() == 4


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
        memory.store(1, 0x100)
    assert excinfo.value.args[0]['value'] == 0x100

def test_msize_initially_zero():
    # 5960005360016000f3
    code = assemble(
    [               # stack     | memory    | note
        MSIZE,      # 0         |           | memory size in bytes (0 active words)
        PUSH1, 0,   # 0, 0      |           | mem offset
        MSTORE8,    #           | 0         | store memory size
        PUSH1, 1,   # 1         | 0         | mem length
        PUSH1, 0,   # 0, 1      | 0         | mem offset
        RETURN      #           | 0         | return mem[0] = 0
    ])

    ret = run(code, verbose=True)
    assert int.from_bytes(ret, 'big') == 0

def test_msize_incremented_on_mload():
    # 6010515960005360016000f3
    code = assemble(
    [               # stack     | memory    | note
        PUSH1, 16,  # 16        |           | mem offset
        MLOAD,      # 0         | 0         | straddles the first and second words (2 active words)
        MSIZE,      # 64, 0     | 0         | memory size in bytes
        PUSH1, 0,   # 0, 64, 0  | 0         | mem offset
        MSTORE8,    # 0         | 64        | store memory size
        PUSH1, 1,   # 1, 0      | 64        | mem length
        PUSH1, 0,   # 0, 1, 0   | 64        | mem offset
        RETURN      # 0         | 64        | return mem[0] = 64
    ])

    ret = run(code)
    assert int.from_bytes(ret, 'big') == 64