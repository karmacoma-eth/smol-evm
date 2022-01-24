class Stack:
    def __init__(self) -> None:
        self.stack = []

    def push(self, item: int) -> None:
        if item < 0 or item > 2**256:
            raise Exception("Stack item must be uint256")

        if (len(self.stack) + 1) > 1024:
            raise Exception("Stack overflow")

        self.stack.append(item)

    def pop(self) -> int:
        if (len(self.stack) == 0):
            raise Exception("Stack underflow")

        return self.stack.pop()

    def __str__(self) -> str:
        return str(self.stack)

    def __repr__(self) -> str:
        return str(self)