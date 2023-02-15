from disasm import disassemble
from smol_evm.opcodes import *


def test_simple():
    code = assemble([PUSH(0x4243)])
    disassembly = disassemble(code)
    assert disassembly == ["0000: PUSH2 0x4243"]
    assert code == assemble(disassembly)


def test_medatata_parsed_as_data():
    code = assemble([REVERT, 1, 2, 3])
    disassembly = disassemble(code)
    assert disassembly == ["0000: REVERT", "0001: DATA 0x01", "0002: DATA 0x02", "0003: DATA 0x03"]
    assert code == assemble(disassembly)


def test_jumpdest_in_metadata():
    code = assemble([REVERT, 1, 2, 3, JUMPDEST])
    disassembly = disassemble(code)
    assert disassembly == [
        "0000: REVERT",
        "0001: DATA 0x01",
        "0002: DATA 0x02",
        "0003: DATA 0x03",
        "0004: JUMPDEST",
    ]
    assert code == assemble(disassembly)


def test_code_after_jumpdest_in_metadata():
    code = assemble([REVERT, 1, JUMPDEST, STOP])
    disassembly = disassemble(code)
    assert disassembly == ['0000: REVERT', '0001: DATA 0x01', '0002: JUMPDEST', '0003: STOP']
    assert code == assemble(disassembly)


def test_jumpdest_in_push_arg():
    code = assemble([REVERT, PUSH(JUMPDEST.opcode), 1, 2, 3])
    disassembly = disassemble(code)
    assert all("JUMPDEST" not in line for line in disassembly)
    assert code == assemble(disassembly)


def test_truncated_push_handled_in_code():
    code = assemble([PUSH(0x4243)])

    # drop the last byte
    code = code[:-1]

    disassembly = disassemble(code)
    assert disassembly == ['0000: PUSH2 0x42 # truncated']
    assert code == assemble(disassembly)


def test_truncated_push_handled_in_metadata():
    code = assemble([REVERT, 1, PUSH(0x5b43)])

    # drop the last byte
    code = code[:-1]

    disassembly = disassemble(code)
    assert disassembly == ['0000: REVERT', '0001: DATA 0x01', '0002: DATA 0x61', '0003: DATA 0x5b']
    assert code == assemble(disassembly)


def test_handles_unknown_opcodes():
    code = assemble([0xfc, PUSH(0xfc), STOP, 0xfc])
    disassembly = disassemble(code)
    assert disassembly == ['0000: UNKNOWN 0xfc', '0001: PUSH1 0xfc', '0003: STOP', '0004: DATA 0xfc']
    assert code == assemble(disassembly)


def test_data_after_jump():
    code = assemble([PUSH(0), JUMP, 1, 2, 3])
    disassembly = disassemble(code)
    assert disassembly == ['0000: PUSH1 0x00', '0002: JUMP', '0003: DATA 0x01', '0004: DATA 0x02', '0005: DATA 0x03']
    assert code == assemble(disassembly)


def test_living_dangerously():
    code = assemble([CALLVALUE, JUMP, JUMPDEST, STOP, 1, 2, 3, JUMPDEST, SELFDESTRUCT])
    disassembly = disassemble(code)
    assert disassembly == [
        '0000: CALLVALUE',
        '0001: JUMP',
        '0002: JUMPDEST',
        '0003: STOP',
        '0004: DATA 0x01',
        '0005: DATA 0x02',
        '0006: DATA 0x03',
        '0007: JUMPDEST',
        '0008: SELFDESTRUCT',
    ]
    assert code == assemble(disassembly)

