from dataclasses import dataclass
from typing import Sequence, Union

from .constants import MAX_UINT256
from .context import ExecutionContext
from .exceptions import InvalidCodeOffset, UnknownOpcode, InvalidJumpDestination


class Instruction:
    def __init__(self, opcode: int, name: str, arg_length=0):
        self.opcode = opcode
        self.name = name
        self.arg_length = arg_length

    def execute(self, context: ExecutionContext) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class DuplicateOpcode(Exception):
    ...


INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}
PUSH_OPCODES = set()


def instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func
    INSTRUCTIONS.append(instruction)

    if opcode in INSTRUCTIONS_BY_OPCODE:
        raise DuplicateOpcode({"opcode": opcode})
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction

    if name.startswith("PUSH"):
        PUSH_OPCODES.add(opcode)

    return instruction


def _do_jump(ctx: ExecutionContext, target_pc: int) -> None:
    if target_pc not in ctx.jumpdests:
        raise InvalidJumpDestination(target_pc=target_pc, context=ctx)
    ctx.set_program_counter(target_pc)


def execute_JUMP(ctx: ExecutionContext) -> None:
    _do_jump(ctx, ctx.stack.pop())


def execute_JUMPI(ctx: ExecutionContext) -> None:
    target_pc, cond = ctx.stack.pop(), ctx.stack.pop()
    if cond != 0:
        _do_jump(ctx, target_pc)


STOP = instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
PUSH1 = instruction(
    0x60,
    "PUSH1",
    (lambda ctx: ctx.stack.push(ctx.read_code(1))),
)
ADD = instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) % 2 ** 256)),
)
MUL = instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) % 2 ** 256)),
)
MSTORE8 = instruction(
    0x53,
    "MSTORE8",
    (lambda ctx: ctx.memory.store(ctx.stack.pop(), ctx.stack.pop() % 256)),
)
RETURN = instruction(
    0xF3,
    "RETURN",
    (lambda ctx: ctx.set_return_data(ctx.stack.pop(), ctx.stack.pop())),
)
JUMP = instruction(
    0x56,
    "JUMP",
    execute_JUMP,
)
JUMPI = instruction(
    0x57,
    "JUMPI",
    execute_JUMPI,
)
PC = instruction(
    0x58,
    "PC",
    (lambda ctx: ctx.stack.push(ctx.pc)),
)
JUMPDEST = instruction(
    0x5B,
    "JUMPDEST",
    # This operation has no effect on machine state during execution.
    (lambda ctx: ctx),
)


def decode_opcode(self) -> Instruction:
    if self.pc < 0:
        raise InvalidCodeOffset({"code": self.code.hex(), "pc": self.pc})

    # section 9.4.1 of the yellow paper, if pc is outside code, then the operation to be executed is STOP
    if self.pc >= len(self.code):
        return STOP

    opcode = self.read_code(1)
    instruction = INSTRUCTIONS_BY_OPCODE.get(opcode)
    if instruction is None:
        raise UnknownOpcode({"opcode": opcode}, content=self)

    return instruction


def assemble(instructions: Sequence[Union[Instruction, int]], print_bin=True) -> bytes:
    result = bytes()
    for item in instructions:
        if isinstance(item, Instruction):
            result += bytes([item.opcode])
        elif isinstance(item, int):
            result += int_to_bytes(item)
        else:
            raise TypeError(f"Unexpected {type(item)} in {instructions}")

    if print_bin:
        print(result.hex())

    return result


# thanks, https://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3
def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(max(1, (x.bit_length() + 7) // 8), "big")
