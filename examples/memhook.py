"""This example shows how to hook and hijack memory writes"""

from smol_evm.opcodes import *
from smol_evm.runner import run

def prehook(context, instruction):
    if instruction.opcode == MSTORE.opcode:
        offset, expected = context.stack.pop(), context.stack.pop()
        hijacked = 0xdeadbeef
        context.stack.push(hijacked)
        context.stack.push(offset)
        print(f"MSTORE hijacker replaced stack contents with {hijacked:x} (was {expected:x})")

code = assemble([
    PUSH(0x42),
    PUSH(0),
    MSTORE,
    PUSH(0x20),
    PUSH(0),
    RETURN,
], print_bin=False)

ret = run(code, verbose=False).returndata
print("unmodified return value:", ret.hex())

ret = run(code, verbose=False, prehook=prehook).returndata
print("hijacked return value:", ret.hex())
