from dataclasses import dataclass

from .context import ExecutionContext, Calldata
from .opcodes import decode_opcode


@dataclass
class ExecutionLimitReached(Exception):
    context: ExecutionContext


def run(code: bytes, calldata=bytes(), verbose=False, max_steps=0, prehook=None, posthook=None) -> None:
    """
    Executes code in a fresh context.
    """
    context = ExecutionContext(code=code, calldata=Calldata(calldata))
    num_steps = 0

    while not context.stopped:
        pc_before = context.pc
        instruction = decode_opcode(context)

        if prehook:
            prehook(context, instruction)

        instruction.execute(context)

        if posthook:
            posthook(context, instruction)

        num_steps += 1
        if max_steps > 0 and num_steps > max_steps:
            raise ExecutionLimitReached(context=context)

        if verbose:
            print(f"{instruction} @ pc={pc_before}")
            print(f"stack: [{', '.join(hex(x) for x in context.stack.stack)}]")
            print()

    if verbose:
        print(f"Output: 0x{context.returndata.hex()}")

    return context.returndata
