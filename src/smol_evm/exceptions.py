from dataclasses import dataclass

from smol_evm.context import ExecutionContext


@dataclass
class EVMException(Exception):
    context: ExecutionContext


@dataclass
class UnknownOpcode(EVMException):
    opcode: int

    def __str__(self):
        return f"opcode={hex(self.opcode)}, context={self.context}"


@dataclass
class InvalidCodeOffset(EVMException):
    offset: int

    def __str__(self):
        return f"offset={hex(self.opcode)}, context={self.context}"


@dataclass
class InvalidJumpDestination(EVMException):
    target_pc: int

    def __str__(self):
        return f"target_pc={hex(self.opcode)}, context={self.context}"
