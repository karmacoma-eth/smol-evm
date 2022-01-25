from .context import ExecutionContext
from .opcodes import decode_opcode


def run(code: bytes) -> None:
    """
    Executes code in a fresh context.
    """
    context = ExecutionContext(code=code)

    while not context.stopped:
        pc_before = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)

        print(f"{instruction} @ pc={pc_before}")
        print(context)
        print()

    print(f'Output: 0x{context.returndata.hex()}')
