from .memory import Memory
from .stack import Stack


class ExecutionContext:
    def __init__(self, code=bytes(), pc=0, stack=Stack(), memory=Memory()) -> None:
        self.code = code
        self.stack = stack
        self.memory = memory
        self.pc = pc
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True

    def read_next_bytes(self, num) -> int:
        value = int.from_bytes(self.code[self.pc : self.pc + num], byteorder="big")
        self.pc += num
        return value

    def __str__(self) -> str:
        return "stack: " + str(self.stack) + "\nmemory: " + str(self.memory)

    def __repr__(self) -> str:
        return str(self)
