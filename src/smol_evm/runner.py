from dataclasses import dataclass

from .context import ExecutionContext
from .opcodes import decode_opcode


@dataclass
class ExecutionLimitReached(Exception):
    context: ExecutionContext


def run(code: bytes, verbose=False, max_steps=0) -> None:
    """
    Executes code in a fresh context.
    """
    context = ExecutionContext(code=code)
    num_steps = 0

    while not context.stopped:
        pc_before = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)

        num_steps += 1
        if max_steps > 0 and num_steps > max_steps:
            raise ExecutionLimitReached(context=context)

        if verbose:
            print(f"{instruction} @ pc={pc_before}")
            print(context)
            print()

    if verbose:
        print(f"Output: 0x{context.returndata.hex()}")

    return context.returndata
