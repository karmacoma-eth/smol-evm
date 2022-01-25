from .context import ExecutionContext


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


class UnknownOpcode(Exception):
    ...


class InvalidCodeOffset(Exception):
    ...


INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}


def register_instruction(opcode: int, name: str, execute_func: callable):
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func
    INSTRUCTIONS.append(instruction)

    assert opcode not in INSTRUCTIONS_BY_OPCODE
    INSTRUCTIONS_BY_OPCODE[opcode] = instruction

    return instruction


STOP = register_instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
PUSH1 = register_instruction(
    0x60,
    "PUSH1",
    (lambda ctx: ctx.stack.push(ctx.read_next_bytes(1))),
)
ADD = register_instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push(ctx.stack.pop() + ctx.stack.pop())),
)
MUL = register_instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push(ctx.stack.pop() * ctx.stack.pop())),
)


def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0 or context.pc >= len(context.code):
        raise InvalidCodeOffset({"code": context.code, "pc": context.pc})

    opcode = context.read_next_bytes(1)
    instruction = INSTRUCTIONS_BY_OPCODE.get(opcode)
    if instruction is None:
        raise UnknownOpcode({"opcode": opcode})

    return instruction
