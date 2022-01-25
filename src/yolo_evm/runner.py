from .context import ExecutionContext
from .opcodes import decode_opcode


def run(code: bytes) -> None:
    """
    Executes the code in a fresh context.
    """

    context = ExecutionContext(code=code)

    while not context.stopped:
        instruction = decode_opcode(context)

        instruction.execute(context)

        print(f'{instruction} @ pc={context.pc}')
        print(context)
        print()