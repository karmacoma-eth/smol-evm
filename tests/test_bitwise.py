from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import AND,OR,XOR,NOT,SHL,SHR,SAR,BYTE

import pytest

from shared import with_stack

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_or_simple(context):
    OR(with_stack(context,[int("0x1F",16),int("0xF0",16)]))
    assert context.stack.pop() == int("0xFF",16)


def test_and_simple(context):
    AND(with_stack(context,[int("0x1F",16),int("0xF0",16)]))
    assert context.stack.pop() == int("0x10",16)


def test_xor_simple(context):
    XOR(with_stack(context,[int("0x1F",16),int("0xF0",16)]))
    assert context.stack.pop() == int("0xEF",16)


def test_not_simple(context):
    NOT(with_stack(context, [1]))
    assert context.stack.pop() == int("0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe",16)


def test_shl_simple(context):
    SHL(with_stack(context, [16, 1]))
    assert context.stack.pop() == 32


def test_shl_big(context):
    SHL(with_stack(context, [16, 5]))
    assert context.stack.pop() == 512


def test_shl_by_zero(context):
    SHL(with_stack(context, [16, 0]))
    assert context.stack.pop() == 16


def test_shl_non_power_of_two(context):
    SHL(with_stack(context, [15, 1]))
    assert context.stack.pop() == 30


def test_shl_max(context):
    SHL(with_stack(context, [2 ** 256 - 1, 1]))
    assert context.stack.pop() == (2 ** 256 - 1) - 1


def test_shl_by_max(context):
    SHL(with_stack(context, [2 ** 256 - 1, 2 ** 256 - 1]))
    assert context.stack.pop() == 0


def test_shr_simple(context):
    SHR(with_stack(context, [16, 1]))
    assert context.stack.pop() == 8


def test_shr_big(context):
    SHR(with_stack(context, [16, 5]))
    assert context.stack.pop() == 0


def test_shr_by_zero(context):
    SHR(with_stack(context, [16, 0]))
    assert context.stack.pop() == 16


def test_shr_non_power_of_two(context):
    SHR(with_stack(context, [15, 1]))
    assert context.stack.pop() == 7


def test_sar(context):
    SAR(with_stack(context,[0x80000000000000000000000000000000000000000000000000000000000000ff,2]))
    assert context.stack.pop() == 0xe00000000000000000000000000000000000000000000000000000000000003f

    SAR(with_stack(context,[0x70000000000000000000000000000000000000000000000000000000000000ff,2]))
    assert context.stack.pop() == 0x1c0000000000000000000000000000000000000000000000000000000000003f

def test_byte(context):
    BYTE(with_stack(context, [0xABCDEF0908070605040302010000000000000000000000000000000000000000, 0]))
    assert context.stack.pop() == 0xAB

    BYTE(with_stack(context, [0xABCDEF0908070605040302010000000000000000000000000000000000000000, 1]))
    assert context.stack.pop() == 0xCD

    BYTE(with_stack(context, [0x00CDEF090807060504030201ffffffffffffffffffffffffffffffffffffffff, 0]))
    assert context.stack.pop() == 0x00

    BYTE(with_stack(context, [0x00CDEF090807060504030201ffffffffffffffffffffffffffffffffffffffff, 1]))
    assert context.stack.pop() == 0xCD

    BYTE(with_stack(context, [0x0000000000000000000000000000000000000000000000000000000000102030, 31]))
    assert context.stack.pop() == 0x30

    BYTE(with_stack(context, [0x0000000000000000000000000000000000000000000000000000000000102030, 30]))
    assert context.stack.pop() == 0x20

    BYTE(with_stack(context, [0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 32]))
    assert context.stack.pop() == 0x00

    BYTE(with_stack(context, [0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 255]))
    assert context.stack.pop() == 0x00
