from .memory import Memory
from .stack import Stack

class ExecutionContext:
    def __init__(self) -> None:
        self.stack = Stack()
        self.memory = Memory()
        self.pc = 0
        self.stopped = False

    def __str__(self) -> str:
        return 'stack: ' + str(self.stack) + '\nmemory: ' + str(self.memory)

    def __repr__(self) -> str:
        return str(self)