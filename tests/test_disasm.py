from disasm import disassemble
from smol_evm.opcodes import *


def test_simple():
    code = assemble([PUSH(0x4243)])
    disassembly = disassemble(code)
    assert disassembly == ["0000: PUSH2 0x4243"]


def test_medatata_parsed_as_data():
    code = assemble([REVERT, 1, 2, 3])
    disassembly = disassemble(code)
    assert disassembly == ["0000: REVERT", "0001: DATA 0x01", "0002: DATA 0x02", "0003: DATA 0x03"]


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


def test_code_after_jumpdest_in_metadata():
    code = assemble([REVERT, 1, JUMPDEST, STOP])
    disassembly = disassemble(code)
    assert disassembly == ['0000: REVERT', '0001: DATA 0x01', '0002: JUMPDEST', '0003: STOP']


def test_jumpdest_in_push_arg():
    code = assemble([REVERT, PUSH(JUMPDEST.opcode), 1, 2, 3])
    disassembly = disassemble(code)
    assert all("JUMPDEST" not in line for line in disassembly)


def test_truncated_push_handled_in_code():
    code = assemble([PUSH(0x4243)])

    # drop the last byte
    code = code[:-1]

    disassembly = disassemble(code)
    assert disassembly == ['0000: PUSH2 0x42 # truncated']


def test_truncated_push_handled_in_metadata():
    code = assemble([REVERT, 1, PUSH(0x5b43)])

    # drop the last byte
    code = code[:-1]

    disassembly = disassemble(code)
    assert disassembly == ['0000: REVERT', '0001: DATA 0x01', '0002: DATA 0x61', '0003: DATA 0x5b']


def test_handles_unknown_opcodes():
    code = assemble([0xfc, PUSH(0xfc), STOP, 0xfc])
    disassembly = disassemble(code)
    assert disassembly == ['0000: UNKNOWN 0xfc', '0001: PUSH1 0xfc', '0003: STOP', '0004: DATA 0xfc']
