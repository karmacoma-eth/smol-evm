import functools
import os
import sys

from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Union
from eth_utils import keccak
from math import ceil

from .context import ExecutionContext
from .exceptions import InvalidCodeOffset, UnknownOpcode, InvalidJumpDestination
from .constants import MAX_UINT256

PUSH1_OPCODE = 0x60
PUSH32_OPCODE = 0x7F


class Operand:
    """
    A class that represents a numeric operand in an instruction.
    """

    def __init__(self, width: int, value: int):
        """
        :param width: the width of the operand in bytes
        :param value: the value of the operand
        """
        self.width = width
        self.value = value

    def __str__(self) -> str:
        format_str = f"0x{{:0{self.width * 2}x}}"
        arg_str = f" {format_str.format(self.value)}"
        return arg_str

    def __repr__(self) -> str:
        return f"Operand({self.width}, {self.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Operand):
            return False
        return self.width == other.width and self.value == other.value

    def __iter__(self):
        value_bytes = int_to_bytes(self.value)
        # pad the value with zeros to the width of the operand
        return iter(bytes(self.width - len(value_bytes)) + value_bytes)


class Instruction:
    def __init__(self, opcode: int, name: str, operands: Sequence[Operand] = ()):
        self.opcode = opcode
        self.name = name
        self.operands = operands

    def __str__(self) -> str:
        return self.name + " ".join([str(x) for x in self.operands])

    def __repr__(self) -> str:
        return (
            f'Instruction({self.opcode}, "{self.name}", {self.operands})'
            if self.operands
            else f'Instruction({self.opcode}, "{self.name}")'
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Instruction):
            return False
        return self.opcode == other.opcode and self.operands == other.operands

    def execute(self, context: ExecutionContext) -> None:
        if self.is_push():
            if self.operands:
                context.stack.push(self.operands[0].value)
            else:
                # this instruction has not been materialized, grab the operand from the context's code
                context.stack.push(context.read_code(self.push_width()))

        else:
            raise NotImplementedError

    def is_push(self) -> bool:
        """
        returns true if this instruction's opcode is between the opcodes of PUSH1 and PUSH32
        """
        return PUSH1_OPCODE <= self.opcode <= PUSH32_OPCODE

    def push_width(self) -> int:
        return self.opcode - PUSH1_OPCODE + 1 if self.is_push() else 0

    def to_bytes(self) -> bytes:
        """
        Returns the bytes that represent this instruction.
        """
        if self.operands:
            return bytes([self.opcode]) + int_to_bytes(self.operands[0].value)
        else:
            return bytes([self.opcode])


class DuplicateOpcode(Exception):
    ...


class InstructionRegistry:
    def __init__(self):
        self.by_code = [None] * 256
        self.by_name = {}
        self.by_func = {}

    def __getitem__(self, item: Union[int, str, object]) -> Optional[Instruction]:
        if isinstance(item, int):
            retrieved = self.by_code[item]
            return retrieved

        if isinstance(item, str):
            return self.by_name[item]

        if callable(item):
            return self.by_func[item]

        raise TypeError(f"Unexpected type for instruction lookup: {type(item)}")

    def __iter__(self):
        return iter([i for i in self.by_code if i is not None])

    def __len__(self):
        return len(self.by_name)

    def add(self, instruction: Instruction):
        if self.by_code[instruction.opcode] is not None:
            raise DuplicateOpcode({"opcode": instruction.opcode})

        self.by_code[instruction.opcode] = instruction
        self.by_name[instruction.name] = instruction
        self.by_func[instruction.execute] = instruction


REGISTRY = InstructionRegistry()


def instruction(opcode: int, name: str, func: Callable[[ExecutionContext], None]):
    instruction = Instruction(opcode, name)
    instruction.execute = func

    REGISTRY.add(instruction)

    return instruction


# a decorator for * functions that registers them as instructions
def insn(opcode: int, name: Optional[str] = None):
    def decorator_insn(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        i = instruction(opcode, name or func.__name__, wrapped)

        # add the opcode to the function to enable syntactic sugar like PUSH1.opcode
        wrapped.opcode = opcode

        return wrapped

    return decorator_insn


def uint_to_int(n):
    if (n >> 255) != 0:
        return -(MAX_UINT256 + 1 - (n & MAX_UINT256))
    return n & MAX_UINT256


def int_to_uint(n):
    if n < 0:
        n = MAX_UINT256 + n + 1
    return n & MAX_UINT256


@insn(0x00)
def STOP(ctx: ExecutionContext) -> None:
    ctx.stop(success=True)


@insn(0x01)
def ADD(ctx: ExecutionContext) -> None:
    ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) & MAX_UINT256)


@insn(0x02)
def MUL(ctx: ExecutionContext) -> None:
    ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) & MAX_UINT256)


@insn(0x03)
def SUB(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push((a - b) & MAX_UINT256)


@insn(0x04)
def DIV(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(a // b if b != 0 else 0)


@insn(0x05)
def SDIV(ctx: ExecutionContext) -> None:
    a, b = uint_to_int(ctx.stack.pop()), uint_to_int(ctx.stack.pop())
    ctx.stack.push(int_to_uint(a // b) if b != 0 else 0)


@insn(0x06)
def MOD(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(a % b if b != 0 else 0)


@insn(0x07)
def SMOD(ctx: ExecutionContext) -> None:
    a, b = uint_to_int(ctx.stack.pop()), uint_to_int(ctx.stack.pop())
    ctx.stack.push(int_to_uint(a % b) if b != 0 else 0)


@insn(0x08)
def ADDMOD(ctx: ExecutionContext) -> None:
    a, b, mod = ctx.stack.pop(), ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(((a + b) % mod) & MAX_UINT256)


@insn(0x09)
def MULMOD(ctx: ExecutionContext) -> None:
    a, b, mod = ctx.stack.pop(), ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(((a * b) % mod) & MAX_UINT256)


@insn(0x0A)
def EXP(ctx: ExecutionContext) -> None:
    a, exponent = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push((a**exponent) & MAX_UINT256)


@insn(0x0B)
def SIGNEXTEND(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()  # a size in bytes, b int value
    # take rightmost <a+1> bytes of integer b
    b = b & ((1 << (a + 1) * 8) - 1)

    # check if integer b is signed
    if (b >> ((a + 1) * 8 - 1)) != 0:
        # create bitmask of all ones up to first bit of "b" (starting from left)
        # e.g. b = 1010 (0xA) => mask = 1111 1111 ... 1010
        mask = MAX_UINT256 ^ ((1 << (a + 1) * 8) - 1)

        # set all bits left from "b" to one
        b = b | mask

    ctx.stack.push(b)


@insn(0x10)
def LT(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(1 if a < b else 0)


@insn(0x11)
def GT(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(1 if a > b else 0)


@insn(0x12)
def SLT(ctx: ExecutionContext) -> None:
    a, b = uint_to_int(ctx.stack.pop()), uint_to_int(ctx.stack.pop())
    ctx.stack.push(1 if a < b else 0)


@insn(0x13)
def SGT(ctx: ExecutionContext) -> None:
    a, b = uint_to_int(ctx.stack.pop()), uint_to_int(ctx.stack.pop())
    ctx.stack.push(1 if a > b else 0)


@insn(0x14)
def EQ(ctx: ExecutionContext) -> None:
    ctx.stack.push(1 if ctx.stack.pop() == ctx.stack.pop() else 0)


@insn(0x15)
def ISZERO(ctx: ExecutionContext) -> None:
    ctx.stack.push(1 if ctx.stack.pop() == 0 else 0)


@insn(0x16)
def AND(ctx: ExecutionContext) -> None:
    ctx.stack.push((ctx.stack.pop() & ctx.stack.pop()))


@insn(0x17)
def OR(ctx: ExecutionContext) -> None:
    ctx.stack.push((ctx.stack.pop() | ctx.stack.pop()))


@insn(0x18)
def XOR(ctx: ExecutionContext) -> None:
    ctx.stack.push((ctx.stack.pop() ^ ctx.stack.pop()))


@insn(0x19)
def NOT(ctx: ExecutionContext) -> None:
    ctx.stack.push(MAX_UINT256 ^ ctx.stack.pop())


@insn(0x1A)
def BYTE(ctx: ExecutionContext) -> None:
    offset, value = ctx.stack.pop(), ctx.stack.pop()
    if offset < 32:
        ctx.stack.push((value >> ((31 - offset) * 8)) & 0xFF)
    else:
        ctx.stack.push(0)


@insn(0x1B)
def SHL(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(0 if a >= 256 else ((b << a) % 2**256))


@insn(0x1C)
def SHR(ctx: ExecutionContext) -> None:
    a, b = ctx.stack.pop(), ctx.stack.pop()
    ctx.stack.push(b >> a)


@insn(0x1D)
def SAR(ctx: ExecutionContext) -> None:
    shift, signed_value = ctx.stack.pop(), uint_to_int(ctx.stack.pop())
    ctx.stack.push(int_to_uint(signed_value >> shift))


@insn(0x20)
def SHA3(ctx: ExecutionContext) -> None:
    offset, size = ctx.stack.pop(), ctx.stack.pop()
    content = ctx.memory.load_range(offset, size)
    ctx.stack.push(int.from_bytes(keccak(content), "big"))


# TODO: placeholder for now
@insn(0x34)
def CALLVALUE(ctx: ExecutionContext) -> None:
    ctx.stack.push(0)


@insn(0x35)
def CALLDATALOAD(ctx: ExecutionContext) -> None:
    ctx.stack.push(ctx.calldata.read_word(ctx.stack.pop()))


@insn(0x36)
def CALLDATASIZE(ctx: ExecutionContext) -> None:
    ctx.stack.push(len(ctx.calldata))


@insn(0x37)
def CALLDATACOPY(ctx: ExecutionContext) -> None:
    dest_offset, offset, size = ctx.stack.pop(), ctx.stack.pop(), ctx.stack.pop()
    for pos in range((size / 32).__ceil__()):
        ctx.memory.store_word(dest_offset + pos * 32, ctx.calldata.read_word(offset + pos * 32))


@insn(0x3C)
def EXTCODECOPY(ctx: ExecutionContext) -> None:
    address, dest_offset, offset, size = (
        ctx.stack.pop(),
        ctx.stack.pop(),
        ctx.stack.pop(),
        ctx.stack.pop(),
    )

    # TODO: placeholder for now, insert dummy bytes in the target memory
    for i in range(size):
        ctx.memory.store(dest_offset + i, 0x42)


@insn(0x50)
def POP(ctx: ExecutionContext) -> None:
    ctx.stack.pop()


@insn(0x51)
def MLOAD(ctx: ExecutionContext) -> None:
    ctx.stack.push(ctx.memory.load_word(ctx.stack.pop()))


@insn(0x52)
def MSTORE(ctx: ExecutionContext) -> None:
    ctx.memory.store_word(offset=ctx.stack.pop(), value=ctx.stack.pop())


@insn(0x53)
def MSTORE8(ctx: ExecutionContext) -> None:
    ctx.memory.store(offset=ctx.stack.pop(), value=ctx.stack.pop() % 256)


@insn(0x54)
def SLOAD(ctx: ExecutionContext) -> None:
    ctx.stack.push(ctx.storage.get(slot=ctx.stack.pop()))


@insn(0x55)
def SSTORE(ctx: ExecutionContext) -> None:
    ctx.storage.put(slot=ctx.stack.pop(), value=ctx.stack.pop())


def _do_jump(ctx: ExecutionContext, target_pc: int) -> None:
    if target_pc in ctx.jumpdests:
        ctx.set_program_counter(target_pc)
    else:
        ctx.stop(success=False, reason=f"Invalid jump to {target_pc}, not in valid jumpdests {ctx.jumpdests}")


@insn(0x56)
def JUMP(ctx: ExecutionContext) -> None:
    _do_jump(ctx, ctx.stack.pop())


@insn(0x57)
def JUMPI(ctx: ExecutionContext) -> None:
    target_pc, cond = ctx.stack.pop(), ctx.stack.pop()
    if cond != 0:
        _do_jump(ctx, target_pc)


@insn(0x58)
def PC(ctx: ExecutionContext) -> None:
    """Get the value of the program counter prior to the increment corresponding to this instruction."""
    ctx.stack.push(ctx.pc - 1)


@insn(0x59)
def MSIZE(ctx: ExecutionContext) -> None:
    ctx.stack.push(32 * ctx.memory.active_words())


# TODO: placeholder for now
@insn(0x5A)
def GAS(ctx: ExecutionContext) -> None:
    """Get the amount of available gas, including the corresponding reduction for the cost of this instruction."""
    ctx.stack.push(MAX_UINT256)


@insn(0x5B)
def JUMPDEST(ctx: ExecutionContext) -> None:
    """Mark a valid destination for jumps. This operation has no effect on machine state during execution."""
    pass


# register PUSH instructions
for i in range(0, 32):
    PUSHi = Instruction(PUSH1_OPCODE + i, "PUSH{}".format(i + 1))
    # print(f"registering {PUSHi.name} with opcode {PUSHi.opcode:02x}")
    REGISTRY.add(PUSHi)

DUP1 = insn(0x80, "DUP1")(lambda ctx: ctx.stack.push(ctx.stack.peek(0)))
DUP2 = insn(0x81, "DUP2")(lambda ctx: ctx.stack.push(ctx.stack.peek(1)))
DUP3 = insn(0x82, "DUP3")(lambda ctx: ctx.stack.push(ctx.stack.peek(2)))
DUP4 = insn(0x83, "DUP4")(lambda ctx: ctx.stack.push(ctx.stack.peek(3)))
DUP5 = insn(0x84, "DUP5")(lambda ctx: ctx.stack.push(ctx.stack.peek(4)))
DUP6 = insn(0x85, "DUP6")(lambda ctx: ctx.stack.push(ctx.stack.peek(5)))
DUP7 = insn(0x86, "DUP7")(lambda ctx: ctx.stack.push(ctx.stack.peek(6)))
DUP8 = insn(0x87, "DUP8")(lambda ctx: ctx.stack.push(ctx.stack.peek(7)))
DUP9 = insn(0x88, "DUP9")(lambda ctx: ctx.stack.push(ctx.stack.peek(8)))
DUP10 = insn(0x89, "DUP10")(lambda ctx: ctx.stack.push(ctx.stack.peek(9)))
DUP11 = insn(0x8A, "DUP11")(lambda ctx: ctx.stack.push(ctx.stack.peek(10)))
DUP12 = insn(0x8B, "DUP12")(lambda ctx: ctx.stack.push(ctx.stack.peek(11)))
DUP13 = insn(0x8C, "DUP13")(lambda ctx: ctx.stack.push(ctx.stack.peek(12)))
DUP14 = insn(0x8D, "DUP14")(lambda ctx: ctx.stack.push(ctx.stack.peek(13)))
DUP15 = insn(0x8E, "DUP15")(lambda ctx: ctx.stack.push(ctx.stack.peek(14)))
DUP16 = insn(0x8F, "DUP16")(lambda ctx: ctx.stack.push(ctx.stack.peek(15)))

SWAP1 = insn(0x90, "SWAP1")(lambda ctx: ctx.stack.swap(1))
SWAP2 = insn(0x91, "SWAP2")(lambda ctx: ctx.stack.swap(2))
SWAP3 = insn(0x92, "SWAP3")(lambda ctx: ctx.stack.swap(3))
SWAP4 = insn(0x93, "SWAP4")(lambda ctx: ctx.stack.swap(4))
SWAP5 = insn(0x94, "SWAP5")(lambda ctx: ctx.stack.swap(5))
SWAP6 = insn(0x95, "SWAP6")(lambda ctx: ctx.stack.swap(6))
SWAP7 = insn(0x96, "SWAP7")(lambda ctx: ctx.stack.swap(7))
SWAP8 = insn(0x97, "SWAP8")(lambda ctx: ctx.stack.swap(8))
SWAP9 = insn(0x98, "SWAP9")(lambda ctx: ctx.stack.swap(9))
SWAP10 = insn(0x99, "SWAP10")(lambda ctx: ctx.stack.swap(10))
SWAP11 = insn(0x9A, "SWAP11")(lambda ctx: ctx.stack.swap(11))
SWAP12 = insn(0x9B, "SWAP12")(lambda ctx: ctx.stack.swap(12))
SWAP13 = insn(0x9C, "SWAP13")(lambda ctx: ctx.stack.swap(13))
SWAP14 = insn(0x9D, "SWAP14")(lambda ctx: ctx.stack.swap(14))
SWAP15 = insn(0x9E, "SWAP15")(lambda ctx: ctx.stack.swap(15))
SWAP16 = insn(0x9F, "SWAP16")(lambda ctx: ctx.stack.swap(16))


@insn(0xF3)
def RETURN(ctx: ExecutionContext) -> None:
    offset, length = ctx.stack.pop(), ctx.stack.pop()
    ctx.set_return_data(offset, length)
    ctx.stop(success=True)


# TODO: no-op for now
@insn(0xFD)
def REVERT(ctx: ExecutionContext) -> None:
    offset, length = ctx.stack.pop(), ctx.stack.pop()
    ctx.stop(success=False)


# TODO: no-op for now. Equivalent to REVERT(0, 0) but consumes all available gas
@insn(0xFE)
def INVALID(ctx: ExecutionContext) -> None:
    ctx.stop(success=False)


# TODO: no-op for now
@insn(0xFF)
def SELFDESTRUCT(ctx: ExecutionContext) -> None:
    ctx.stop(success=True)


if os.getenv("DEBUG"):
    print(f"📈 {len(REGISTRY)} instructions completed")
    print(REGISTRY.by_code)


def PUSH(value: int) -> Instruction:
    """
    Returns the PUSH instruction for the given value, using the smallest possible PUSH instruction
    """
    # get the size of value in bytes (1 minimum)
    width = ceil(value.bit_length() / 8) or 1

    push_with_no_operand = REGISTRY[0x60 + width - 1]
    push_with_operand = Instruction(push_with_no_operand.opcode, push_with_no_operand.name, [Operand(width, value)])
    return push_with_operand


def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0:
        raise InvalidCodeOffset(offset=context.pc, context=context)

    # section 9.4.1 of the yellow paper, if pc is outside code, then the operation to be executed is STOP
    if context.pc >= len(context.code):
        return REGISTRY[STOP]

    # increments context.pc
    opcode = context.read_code(1)
    instruction = REGISTRY[opcode]
    if instruction is None:
        return Instruction(opcode, f"UNKNOWN 0x{opcode:02x}")

    # if it's a push, materialize a new instruction with the correct operand
    if instruction.is_push():
        push_width = instruction.push_width()
        value = context.read_code(push_width)

        # preserve the width from the opcode, even if the value has a smaller bit width
        return Instruction(opcode, instruction.name, [Operand(push_width, value)])

    return instruction


def assemble(instructions: Sequence[Union[Instruction, int, object]], print_bin=True) -> bytes:
    result = bytes()
    for item in instructions:
        if isinstance(item, Instruction):
            result += item.to_bytes()
        elif isinstance(item, int):
            result += int_to_bytes(item)
        elif callable(item):
            _instruction = REGISTRY[item]
            result += bytes([_instruction.opcode])
        elif isinstance(item, str):
            # assume this is our assembler syntax, as produced by disasm.py
            # e.g. <offset>: <OPCODE|UNKNOWN|DATA> [operand] [# comment]
            if item.startswith("#"):
                continue

            comment_start = item.find("#")
            if comment_start != -1:
                item = item[:comment_start]

            tokens = item.split(":", 2)
            if len(tokens) > 2:
                raise ValueError(f"Invalid item: {item}")
            elif len(tokens) == 2:
                offset_str, rest = item.split(":")
                offset = int(offset_str.strip(), 16)
                if offset != len(result):
                    # print to stderr
                    print(
                        f"Warning: expected to write at offset {offset_str}, but currently at {len(result):04x}",
                        file=sys.stderr,
                    )
            else:
                rest = item

            tokens = rest.strip().split(" ", 2)
            instruction_str = tokens[0].strip()
            if instruction_str == "UNKNOWN" or instruction_str == "DATA":
                hex_str = tokens[1].strip()
                result += bytes.fromhex(hex_str[2:] if hex_str.startswith("0x") else hex_str)

            else:
                instruction = REGISTRY[instruction_str]

                if not instruction:
                    raise ValueError(f"Unknown instruction {instruction_str}")

                result += instruction.opcode.to_bytes(1, "big")

                if len(tokens) > 1:
                    operand = tokens[1].strip()
                    result += bytes.fromhex(operand[2:] if operand.startswith("0x") else operand)

        else:
            raise TypeError(f"Unexpected {type(item)} in {instructions}")

    if print_bin:
        print(result.hex())

    return result


# thanks, https://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3
def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(max(1, (x.bit_length() + 7) // 8), "big")
