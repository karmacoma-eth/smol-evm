from yolo_evm.context import ExecutionContext
from yolo_evm.exceptions import InvalidJumpDestination
from yolo_evm.opcodes import assemble, JUMP, JUMPI, PC, PUSH1, STOP, JUMPDEST, RETURN, MSTORE8
from yolo_evm.runner import run, ExecutionLimitReached

import pytest

@pytest.fixture
def context() -> ExecutionContext:
    pass

def test_simple_jump():
    """just jump to the JUMPDEST"""
    # 6003565b
    code = assemble([
        PUSH1, 3,
        JUMP,
        JUMPDEST
    ])
    ret = run(code)
    assert ret == b""

def test_jump_hyperspace():
    """jump way out into the void"""
    # 602a56
    code = assemble([
        PUSH1, 42,
        JUMP
    ])
    with pytest.raises(InvalidJumpDestination) as excinfo:
        run(code)
    assert excinfo.value.target_pc == 42

def test_jump_into_push_arg():
    """can only jump on instructions boundaries, so can't fool the EVM by packing a JUMPDEST in a PUSH argument"""
    # 605b600156
    code = assemble([
        PUSH1, JUMPDEST.opcode,
        PUSH1, 1,
        JUMP
    ])
    with pytest.raises(InvalidJumpDestination) as excinfo:
        run(code)
    assert excinfo.value.target_pc == 1

def test_invalid_jump_dest_in_branch_not_taken():
    """we know we can check for invalid jump destinations, but what if we don't take the branch?"""
    # 6000602a57
    code = assemble([
        PUSH1, 0,  # cond
        PUSH1, 42, # target (bad)
        JUMPI
    ])
    ret = run(code)
    assert ret == b""

def test_infinite_loop():
    # 5b600056
    code = assemble([
        JUMPDEST,
        PUSH1, 0,
        JUMP
    ])
    with pytest.raises(ExecutionLimitReached) as excinfo:
        run(code, max_steps=100)

def test_simple_jumpi_not_taken():
    # 6000600f57602a60005360016000f35b
    code = assemble([
        PUSH1, 0,  # cond
        PUSH1, 15, # target
        JUMPI,

        PUSH1, 42, # mem value
        PUSH1, 0,  # mem offset
        MSTORE8,
        PUSH1, 1,  # mem length
        PUSH1, 0,  # mem offset
        RETURN,

        JUMPDEST
    ])

    ret = run(code)
    assert int.from_bytes(ret, 'big') == 42

def test_simple_jumpi_taken():
    """we're going straight to the end"""
    # 6001600f57602a60005360016000f35b
    code = assemble([
        PUSH1, 1,  # cond
        PUSH1, 15, # target
        JUMPI,

        PUSH1, 42, # mem value
        PUSH1, 0,  # mem offset
        MSTORE8,
        PUSH1, 1,  # mem length
        PUSH1, 0,  # mem offset
        RETURN,

        JUMPDEST
    ])

    ret = run(code)
    assert ret == b""
