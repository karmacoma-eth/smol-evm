from sre_constants import MAX_REPEAT
from .constants import MAX_STACK_DEPTH, MAX_UINT256


class Stack:
    def __init__(self, max_depth=MAX_STACK_DEPTH) -> None:
        self.stack = []
        self.max_depth = max_depth

    def push(self, item: int) -> None:
        if item < 0 or item > MAX_UINT256:
            raise InvalidStackItem({"item": item})

        if (len(self.stack) + 1) > self.max_depth:
            raise StackOverflow()

        self.stack.append(item)

    def pop(self) -> int:
        if len(self.stack) == 0:
            raise StackUnderflow()

        return self.stack.pop()

    def peek(self, i: int) -> int:
        """returns a stack element without popping it -- peek(0) is the top element, peek(1) is the next one, etc."""
        if len(self.stack) < i:
            raise StackUnderflow()

        return self.stack[-(i + 1)]

    def swap(self, i: int) -> None:
        """swaps the top of the stack with the i+1th element"""
        if i == 0:
            return

        if len(self.stack) < i:
            raise StackUnderflow()

        self.stack[-1], self.stack[-i - 1] = self.stack[-i - 1], self.stack[-1]

    def __str__(self) -> str:
        return str(self.stack)

    def __repr__(self) -> str:
        return str(self)


class StackUnderflow(Exception):
    ...


class StackOverflow(Exception):
    ...


class InvalidStackItem(Exception):
    ...
