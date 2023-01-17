from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext, Calldata
from smol_evm.opcodes import CALLDATALOAD, CALLDATASIZE , CALLDATACOPY,MLOAD
from shared import with_calldata

import pytest

@pytest.fixture
def calldata() -> Calldata:
    return Calldata()

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()


def test_simple_calldataload(context):
    ctx = with_calldata(context, range(32))
    ctx.stack.push(0)

    CALLDATALOAD(ctx)
    assert ctx.stack.pop() == 0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f


def test_empty_calldataload(context):
    context.stack.push(0)
    CALLDATALOAD(context)
    assert context.stack.pop() == 0


def test_calldataload_uint256_overflow(context):
    # 7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff35
    context.stack.push(MAX_UINT256)
    CALLDATALOAD(context)
    assert context.stack.pop() == 0

def test_calldatasize_empty(context):
    CALLDATASIZE(context)
    assert context.stack.pop() == 0

def test_calldatasize_one(context):
    CALLDATASIZE(with_calldata(context, [0]))
    assert context.stack.pop() == 1


def test_calldataload(context):
    ctx = with_calldata(context, bytearray.fromhex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF11"))
    ctx.stack.push(33)
    ctx.stack.push(0)
    ctx.stack.push(0)
    CALLDATACOPY(ctx)
    # loading word from memory offset 0
    context.stack.push(0)
    MLOAD(context)
    assert context.stack.pop() == int("0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",16)
    # loading word from memory offset 0x20 (32)
    context.stack.push(32)
    MLOAD(context)
    assert context.stack.pop() == int("0x1100000000000000000000000000000000000000000000000000000000000000",16)



