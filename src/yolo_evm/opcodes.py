from dataclasses import dataclass
from typing import Sequence, Union

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


def instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func
    INSTRUCTIONS.append(instruction)

    if opcode in INSTRUCTIONS_BY_OPCODE:
        raise DuplicateOpcode({"opcode": opcode})
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction

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


def execute_SUB(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push((a - b) % 2 ** 256)


STOP = instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
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
SUB = instruction(
    0x03,
    "SUB",
    execute_SUB,
)
MLOAD = instruction(
    0x51,
    "MLOAD",
    (lambda ctx: ctx.stack.push(ctx.memory.load_word(ctx.stack.pop()))),
)
MSTORE = instruction(
    0x52,
    "MSTORE",
    (lambda ctx: ctx.memory.store_word(ctx.stack.pop(), ctx.stack.pop())),
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
MSIZE = instruction(
    0x59,
    "MSIZE",
    (lambda ctx: ctx.stack.push(32 * ctx.memory.active_words())),
)
JUMPDEST = instruction(
    0x5B,
    "JUMPDEST",
    # This operation has no effect on machine state during execution.
    (lambda ctx: ctx),
)

PUSH1 = instruction(0x60, "PUSH1", lambda ctx: ctx.stack.push(ctx.read_code(1)))
PUSH2 = instruction(0x61, "PUSH2", lambda ctx: ctx.stack.push(ctx.read_code(2)))
PUSH3 = instruction(0x62, "PUSH3", lambda ctx: ctx.stack.push(ctx.read_code(3)))
PUSH4 = instruction(0x63, "PUSH4", lambda ctx: ctx.stack.push(ctx.read_code(4)))
PUSH5 = instruction(0x64, "PUSH5", lambda ctx: ctx.stack.push(ctx.read_code(5)))
PUSH6 = instruction(0x65, "PUSH6", lambda ctx: ctx.stack.push(ctx.read_code(6)))
PUSH7 = instruction(0x66, "PUSH7", lambda ctx: ctx.stack.push(ctx.read_code(7)))
PUSH8 = instruction(0x67, "PUSH8", lambda ctx: ctx.stack.push(ctx.read_code(8)))
PUSH9 = instruction(0x68, "PUSH9", lambda ctx: ctx.stack.push(ctx.read_code(9)))
PUSH10 = instruction(0x69, "PUSH10", lambda ctx: ctx.stack.push(ctx.read_code(10)))
PUSH11 = instruction(0x6A, "PUSH11", lambda ctx: ctx.stack.push(ctx.read_code(11)))
PUSH12 = instruction(0x6B, "PUSH12", lambda ctx: ctx.stack.push(ctx.read_code(12)))
PUSH13 = instruction(0x6C, "PUSH13", lambda ctx: ctx.stack.push(ctx.read_code(13)))
PUSH14 = instruction(0x6D, "PUSH14", lambda ctx: ctx.stack.push(ctx.read_code(14)))
PUSH15 = instruction(0x6E, "PUSH15", lambda ctx: ctx.stack.push(ctx.read_code(15)))
PUSH16 = instruction(0x6F, "PUSH16", lambda ctx: ctx.stack.push(ctx.read_code(16)))
PUSH17 = instruction(0x70, "PUSH17", lambda ctx: ctx.stack.push(ctx.read_code(17)))
PUSH18 = instruction(0x71, "PUSH18", lambda ctx: ctx.stack.push(ctx.read_code(18)))
PUSH19 = instruction(0x72, "PUSH19", lambda ctx: ctx.stack.push(ctx.read_code(19)))
PUSH20 = instruction(0x73, "PUSH20", lambda ctx: ctx.stack.push(ctx.read_code(20)))
PUSH21 = instruction(0x74, "PUSH21", lambda ctx: ctx.stack.push(ctx.read_code(21)))
PUSH22 = instruction(0x75, "PUSH22", lambda ctx: ctx.stack.push(ctx.read_code(22)))
PUSH23 = instruction(0x76, "PUSH23", lambda ctx: ctx.stack.push(ctx.read_code(23)))
PUSH24 = instruction(0x77, "PUSH24", lambda ctx: ctx.stack.push(ctx.read_code(24)))
PUSH25 = instruction(0x78, "PUSH25", lambda ctx: ctx.stack.push(ctx.read_code(25)))
PUSH26 = instruction(0x79, "PUSH26", lambda ctx: ctx.stack.push(ctx.read_code(26)))
PUSH27 = instruction(0x7A, "PUSH27", lambda ctx: ctx.stack.push(ctx.read_code(27)))
PUSH28 = instruction(0x7B, "PUSH28", lambda ctx: ctx.stack.push(ctx.read_code(28)))
PUSH29 = instruction(0x7C, "PUSH29", lambda ctx: ctx.stack.push(ctx.read_code(29)))
PUSH30 = instruction(0x7D, "PUSH30", lambda ctx: ctx.stack.push(ctx.read_code(30)))
PUSH31 = instruction(0x7E, "PUSH31", lambda ctx: ctx.stack.push(ctx.read_code(31)))
PUSH32 = instruction(0x7F, "PUSH32", lambda ctx: ctx.stack.push(ctx.read_code(32)))

DUP1 = instruction(0x80, "DUP1", lambda ctx: ctx.stack.push(ctx.stack.peek(0)))
DUP2 = instruction(0x81, "DUP2", lambda ctx: ctx.stack.push(ctx.stack.peek(1)))
DUP3 = instruction(0x82, "DUP3", lambda ctx: ctx.stack.push(ctx.stack.peek(2)))
DUP4 = instruction(0x83, "DUP4", lambda ctx: ctx.stack.push(ctx.stack.peek(3)))
DUP5 = instruction(0x84, "DUP5", lambda ctx: ctx.stack.push(ctx.stack.peek(4)))
DUP6 = instruction(0x85, "DUP6", lambda ctx: ctx.stack.push(ctx.stack.peek(5)))
DUP7 = instruction(0x86, "DUP7", lambda ctx: ctx.stack.push(ctx.stack.peek(6)))
DUP8 = instruction(0x87, "DUP8", lambda ctx: ctx.stack.push(ctx.stack.peek(7)))
DUP9 = instruction(0x88, "DUP9", lambda ctx: ctx.stack.push(ctx.stack.peek(8)))
DUP10 = instruction(0x89, "DUP10", lambda ctx: ctx.stack.push(ctx.stack.peek(9)))
DUP11 = instruction(0x8A, "DUP11", lambda ctx: ctx.stack.push(ctx.stack.peek(10)))
DUP12 = instruction(0x8B, "DUP12", lambda ctx: ctx.stack.push(ctx.stack.peek(11)))
DUP13 = instruction(0x8C, "DUP13", lambda ctx: ctx.stack.push(ctx.stack.peek(12)))
DUP14 = instruction(0x8D, "DUP14", lambda ctx: ctx.stack.push(ctx.stack.peek(13)))
DUP15 = instruction(0x8E, "DUP15", lambda ctx: ctx.stack.push(ctx.stack.peek(14)))
DUP16 = instruction(0x8F, "DUP16", lambda ctx: ctx.stack.push(ctx.stack.peek(15)))

SWAP1 = instruction(0x90, "SWAP1", lambda ctx: ctx.stack.swap(1))
SWAP2 = instruction(0x91, "SWAP2", lambda ctx: ctx.stack.swap(2))
SWAP3 = instruction(0x92, "SWAP3", lambda ctx: ctx.stack.swap(3))
SWAP4 = instruction(0x93, "SWAP4", lambda ctx: ctx.stack.swap(4))
SWAP5 = instruction(0x94, "SWAP5", lambda ctx: ctx.stack.swap(5))
SWAP6 = instruction(0x95, "SWAP6", lambda ctx: ctx.stack.swap(6))
SWAP7 = instruction(0x96, "SWAP7", lambda ctx: ctx.stack.swap(7))
SWAP8 = instruction(0x97, "SWAP8", lambda ctx: ctx.stack.swap(8))
SWAP9 = instruction(0x98, "SWAP9", lambda ctx: ctx.stack.swap(9))
SWAP10 = instruction(0x99, "SWAP10", lambda ctx: ctx.stack.swap(10))
SWAP11 = instruction(0x9A, "SWAP11", lambda ctx: ctx.stack.swap(11))
SWAP12 = instruction(0x9B, "SWAP12", lambda ctx: ctx.stack.swap(12))
SWAP13 = instruction(0x9C, "SWAP13", lambda ctx: ctx.stack.swap(13))
SWAP14 = instruction(0x9D, "SWAP14", lambda ctx: ctx.stack.swap(14))
SWAP15 = instruction(0x9E, "SWAP15", lambda ctx: ctx.stack.swap(15))
SWAP16 = instruction(0x9F, "SWAP16", lambda ctx: ctx.stack.swap(16))


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
