from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import SHL, SHR, BYTE

import pytest

from shared import with_stack_contents

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_shl_simple(context):
    SHL.execute(with_stack_contents(context, [16, 1]))
    assert context.stack.pop() == 32


def test_shl_big(context):
    SHL.execute(with_stack_contents(context, [16, 5]))
    assert context.stack.pop() == 512


def test_shl_by_zero(context):
    SHL.execute(with_stack_contents(context, [16, 0]))
    assert context.stack.pop() == 16


def test_shl_non_power_of_two(context):
    SHL.execute(with_stack_contents(context, [15, 1]))
    assert context.stack.pop() == 30


def test_shl_max(context):
    SHL.execute(with_stack_contents(context, [2 ** 256 - 1, 1]))
    assert context.stack.pop() == (2 ** 256 - 1) - 1


def test_shl_by_max(context):
    SHL.execute(with_stack_contents(context, [2 ** 256 - 1, 2 ** 256 - 1]))
    assert context.stack.pop() == 0


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

def test_byte(context):
    BYTE.execute(with_stack_contents(context, [0xABCDEF0908070605040302010000000000000000000000000000000000000000, 0]))
    assert context.stack.pop() == 0xAB

    BYTE.execute(with_stack_contents(context, [0xABCDEF0908070605040302010000000000000000000000000000000000000000, 1]))
    assert context.stack.pop() == 0xCD

    BYTE.execute(with_stack_contents(context, [0x00CDEF090807060504030201ffffffffffffffffffffffffffffffffffffffff, 0]))
    assert context.stack.pop() == 0x00

    BYTE.execute(with_stack_contents(context, [0x00CDEF090807060504030201ffffffffffffffffffffffffffffffffffffffff, 1]))
    assert context.stack.pop() == 0xCD

    BYTE.execute(with_stack_contents(context, [0x0000000000000000000000000000000000000000000000000000000000102030, 31]))
    assert context.stack.pop() == 0x30

    BYTE.execute(with_stack_contents(context, [0x0000000000000000000000000000000000000000000000000000000000102030, 30]))
    assert context.stack.pop() == 0x20

    BYTE.execute(with_stack_contents(context, [0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 32]))
    assert context.stack.pop() == 0x00

    BYTE.execute(with_stack_contents(context, [0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 255]))
    assert context.stack.pop() == 0x00
