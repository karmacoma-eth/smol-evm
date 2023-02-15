#!/usr/bin/env python3

import argparse
import os

from smol_evm.context import ExecutionContext
from smol_evm.opcodes import decode_opcode, JUMP, STOP, REVERT, RETURN, INVALID, JUMPDEST

from typing import Sequence

TERMINATING = set((JUMP.opcode, STOP.opcode, REVERT.opcode, RETURN.opcode, INVALID.opcode))


def strip_0x(s: str):
    return s[2:] if s and s.startswith("0x") else s


def disassemble(code: bytes) -> Sequence[str]:
    output = []
    reading_code = True
    context = ExecutionContext(code=code)

    while context.pc < len(code):
        original_pc = context.pc
        pc_str = f"{original_pc:04x}"

        # increments pc by instruction length
        insn = decode_opcode(context)
        push_data = code[original_pc + 1 : original_pc + 1 + insn.push_width()] if insn.is_push() else b""

        # switch back to code mode if we encounter a JUMPDEST
        reading_code = reading_code or insn.opcode is JUMPDEST.opcode

        if reading_code:
            if insn.is_push() and len(push_data) < insn.push_width():
                # make sure we handle truncated PUSH arguments
                output.append(f"{pc_str}: PUSH{insn.push_width()} 0x{push_data.hex()} # truncated")
            else:
                output.append(f"{pc_str}: {insn}")

            reading_code = insn.opcode not in TERMINATING

        else:
            # just like the algorithm for valid jump destination validation,
            # we parse PUSH instructions and skip their arguments (so no JUMPDESTs can hide there)
            data = [insn.opcode]
            data.extend(push_data)
            for i, d in enumerate(data):
                output.append(f"{original_pc + i:04x}: DATA 0x{d:02x}")

    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", help="hex data of the code to run", required=True)
    args = parser.parse_args()

    # is it a file? if so, load the contents
    if os.path.exists(args.code):
        with open(args.code, "r") as f:
            code = bytes.fromhex(strip_0x(f.read()))

    else:
        code = bytes.fromhex(strip_0x(args.code))

    print("\n".join(disassemble(code)))


if __name__ == "__main__":
    main()
