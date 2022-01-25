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

    def read_code(self, num_bytes) -> int:
        """
        Returns the next num_bytes from the code buffer (at index pc) as an integer and advances pc by num_bytes.
        """
        value = int.from_bytes(self.code[self.pc : self.pc + num_bytes], byteorder="big")
        self.pc += num_bytes
        return value

    def __str__(self) -> str:
        return "stack: " + str(self.stack) + "\nmemory: " + str(self.memory)

    def __repr__(self) -> str:
        return str(self)
