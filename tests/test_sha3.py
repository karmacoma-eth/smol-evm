from smol_evm.context import ExecutionContext
from smol_evm.opcodes import SHA3

import pytest

from shared import with_stack, with_memory

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_sha3_simple(context):
    SHA3(
        with_stack(
            with_memory(context, 0, [ord(x) for x in ["a", "b", "c"]]),
            [3, 0]
        )
    )
    assert context.stack.pop() == 0x4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45

def test_sha3_offset(context):
    SHA3(
        with_stack(
            with_memory(context, 0, [ord(x) for x in "foobarbaz"]),
            [3, 6]
        )
    )
    assert context.stack.pop() == 0xf2d05ec5c5729fb559780c70a93ca7b4ee2ca37f64e62fa31046b324f60d9447

def test_sha3_empty(context):
    SHA3(with_stack(context, [0, 0]))
    assert context.stack.pop() == 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
