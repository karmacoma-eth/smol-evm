from dataclasses import dataclass
from typing import Sequence, Union

from .context import ExecutionContext
from .exceptions import InvalidCodeOffset, UnknownOpcode, InvalidJumpDestination
from .constants import MAX_UINT256


class Instruction:
    def __init__(self, opcode: int, name: str):
        self.opcode = opcode
        self.name = name

    def execute(self, context: ExecutionContext) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class DuplicateOpcode(Exception):
    ...


INSTRUCTIONS = [None] * 256


def instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func

    if INSTRUCTIONS[opcode] is not None:
        raise DuplicateOpcode({"opcode": opcode})
    INSTRUCTIONS[opcode] = instruction

    return instruction

def uint_to_int(n):
    if (n >> 255) != 0:
        return -(MAX_UINT256 + 1 - (n & MAX_UINT256))
    return n & MAX_UINT256

def int_to_uint(n):
    if n < 0:
        n = MAX_UINT256 + n + 1
    return n & MAX_UINT256

def _do_jump(ctx: ExecutionContext, target_pc: int) -> None:
    if target_pc not in ctx.jumpdests:
        raise InvalidJumpDestination(target_pc=target_pc, context=ctx)
    ctx.set_program_counter(target_pc)


def uint_to_int(n):
    if (n >> 255) != 0:
        return -(MAX_UINT256 + 1 - (n & MAX_UINT256))
    return (n & MAX_UINT256)

def int_to_uint(n):
    if n < 0:
        n = (MAX_UINT256 + n + 1)
    return (n & MAX_UINT256)


def execute_JUMP(ctx: ExecutionContext) -> None:
    _do_jump(ctx, ctx.stack.pop())


def execute_JUMPI(ctx: ExecutionContext) -> None:
    target_pc, cond = ctx.stack.pop(), ctx.stack.pop()
    if cond != 0:
        _do_jump(ctx, target_pc)


def execute_SUB(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push((a - b) & MAX_UINT256)


def execute_LT(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(1 if a < b else 0)


def execute_GT(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(1 if a > b else 0)

def execute_SLT(ctx: ExecutionContext) -> None:
    a, b = uint_to_int(ctx.stack.pop()), uint_to_int(ctx.stack.pop())
    ctx.stack.push(1 if a < b else 0)


def execute_SGT(ctx: ExecutionContext) -> None:
    a, b = uint_to_int(ctx.stack.pop()), uint_to_int(ctx.stack.pop())
    ctx.stack.push(1 if a > b else 0)
    
def execute_SHL(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(0 if a >= 256 else ((b << a) % 2 ** 256))


def execute_SHR(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(b >> a)


def execute_CALLDATACOPY(ctx: ExecutionContext) -> None:
    dest_offset,offset,size = ctx.stack.pop(),ctx.stack.pop(),ctx.stack.pop()
    for pos in range((size / 32).__ceil__()):
        ctx.memory.store_word(dest_offset + pos * 32,ctx.calldata.read_word(offset + pos * 32))


STOP = instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
ADD = instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) & MAX_UINT256)),
)
MUL = instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) & MAX_UINT256)),
)
SUB = instruction(
    0x03,
    "SUB",
    execute_SUB,
)
DIV = instruction(
    0x04,
    "DIV",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() // ctx.stack.pop()) & MAX_UINT256))
)
SDIV = instruction(
    0x05,
    "SDIV",
    (lambda ctx: ctx.stack.push(int_to_uint(uint_to_int(ctx.stack.pop()) // uint_to_int(ctx.stack.pop()))))
)

MOD = instruction(
    0x06,
    "MOD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() % ctx.stack.pop() & MAX_UINT256)))
)

SMOD = instruction(
    0x07,
    "SMOD",
    (lambda ctx: ctx.stack.push(int_to_uint(uint_to_int(ctx.stack.pop()) % uint_to_int(ctx.stack.pop()))))
)

ADDMOD = instruction(
    0x08,
    "ADDMOD",
    (lambda ctx: ctx.stack.push(((ctx.stack.pop() + ctx.stack.pop()) % ctx.stack.pop()) & MAX_UINT256))
)

MULMOD = instruction(
    0x09,
    "MULMOD",
    (lambda ctx: ctx.stack.push(((ctx.stack.pop() * ctx.stack.pop()) % ctx.stack.pop()) & MAX_UINT256))
)

EXP = instruction(
    0x0A,
    "EXP",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() ** ctx.stack.pop()) & MAX_UINT256))
)

LT = instruction(0x10, "LT", execute_LT)
GT = instruction(0x11, "GT", execute_GT)
SLT = instruction(0x12, "SLT", execute_SLT)
SGT = instruction(0x13, "SGT", execute_SGT)
EQ = instruction(
    0x14,
    "EQ",
    lambda ctx: ctx.stack.push(1 if ctx.stack.pop() == ctx.stack.pop() else 0),
)
ISZERO = instruction(
    0x15,
    "ISZERO",
    lambda ctx: ctx.stack.push(1 if ctx.stack.pop() == 0 else 0),
)
AND = instruction(
    0x16, "AND", (lambda ctx: ctx.stack.push((ctx.stack.pop() & ctx.stack.pop())))
)
OR = instruction(
    0x17, "OR", (lambda ctx: ctx.stack.push((ctx.stack.pop() | ctx.stack.pop())))
)
XOR = instruction(
    0x18, "XOR", (lambda ctx: ctx.stack.push((ctx.stack.pop() ^ ctx.stack.pop())))
)
NOT = instruction(
    0x19, "NOT", (lambda ctx: ctx.stack.push(MAX_UINT256 ^ ctx.stack.pop()))
)
SHL = instruction(
    0x1B,
    "SHL",
    execute_SHL,
)
SHR = instruction(
    0x1C,
    "SHR",
    execute_SHR,
)

# TODO: placeholder for now
CALLVALUE = instruction(
    0x34,
    "CALLVALUE",
    lambda ctx: ctx.stack.push(0),
)
CALLDATALOAD = instruction(
    0x35,
    "CALLDATALOAD",
    lambda ctx: ctx.stack.push(ctx.calldata.read_word(ctx.stack.pop())),
)
CALLDATASIZE = instruction(
    0x36,
    "CALLDATASIZE",
    lambda ctx: ctx.stack.push(len(ctx.calldata)),
)
CALLDATACOPY = instruction(
    0x37,
    "CALLDATACOPY",
    execute_CALLDATACOPY,
)
POP = instruction(
    0x50,
    "POP",
    lambda ctx: ctx.stack.pop(),
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
SLOAD = instruction(
    0x54,
    "SLOAD",
    (lambda ctx: ctx.stack.push(ctx.storage.get(ctx.stack.pop()))),
)
SSTORE = instruction(
    0x55,
    "SSTORE",
    (lambda ctx: ctx.storage.put(ctx.stack.pop(), ctx.stack.pop())),
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

RETURN = instruction(
    0xF3,
    "RETURN",
    (lambda ctx: ctx.set_return_data(ctx.stack.pop(), ctx.stack.pop())),
)

# TODO: no-op for now
REVERT = instruction(0xFD, "REVERT", (lambda ctx: ctx.stop()))


def decode_opcode(context) -> Instruction:
    if context.pc < 0:
        raise InvalidCodeOffset({"code": context.code.hex(), "pc": context.pc})

    # section 9.4.1 of the yellow paper, if pc is outside code, then the operation to be executed is STOP
    if context.pc >= len(context.code):
        return STOP

    opcode = context.read_code(1)
    instruction = INSTRUCTIONS[opcode]
    if instruction is None:
        raise UnknownOpcode(opcode=opcode, context=context)

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
