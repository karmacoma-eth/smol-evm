from .constants import is_valid_uint256
from .memory import Memory
from .stack import Stack


class InvalidCalldataAccess(Exception):
    ...


class InvalidStorageSlot(Exception):
    ...


class InvalidStorageValue(Exception):
    ...


# see yellow paper section 9.4.3
def valid_jump_destinations(code: bytes) -> set[int]:
    from .opcodes import JUMPDEST, PUSH1, PUSH32

    jumpdests = set()
    i = 0
    while i < len(code):
        current_op = code[i]
        if current_op == JUMPDEST.opcode:
            jumpdests.add(i)
        elif PUSH1.opcode <= current_op <= PUSH32.opcode:
            i += current_op - PUSH1.opcode + 1

        i += 1
    return jumpdests


class Calldata:
    def __init__(self, data=bytes()) -> None:
        self.data = data

    def read_byte(self, offset: int) -> int:
        if offset < 0:
            raise InvalidCalldataAccess({"offset": offset})

        return self.data[offset] if offset < len(self.data) else 0

    def read_word(self, offset: int) -> int:
        return int.from_bytes(
            [self.read_byte(x) for x in range(offset, offset + 32)], "big"
        )

    def __len__(self) -> int:
        return len(self.data)


class ExecutionContext:
    def __init__(
        self, code=bytes(), pc=0, stack=None, memory=None, calldata=None, storage=None
    ) -> None:
        self.code = code
        self.stack = stack if stack else Stack()
        self.memory = memory if memory else Memory()
        self.pc = pc
        self.success = None
        self.returndata = bytes()
        self.jumpdests = valid_jump_destinations(code)
        self.calldata = calldata if calldata else Calldata()
        self.storage = storage if storage else Storage()

    def set_return_data(self, offset: int, length: int) -> None:
        self.success = True
        self.returndata = self.memory.load_range(offset, length)

    def stop(self, success: bool) -> None:
        self.success = success

    def is_stopped(self) -> bool:
        return self.success is not None

    def read_code(self, num_bytes) -> int:
        """
        Returns the next num_bytes from the code buffer (at index pc) as an integer and advances pc by num_bytes.
        """
        value = int.from_bytes(
            self.code[self.pc : self.pc + num_bytes], byteorder="big"
        )
        self.pc += num_bytes
        return value

    def set_program_counter(self, pc: int) -> None:
        self.pc = pc

    def __str__(self) -> str:
        return "stack: " + str(self.stack) + "\nmemory: " + str(self.memory)

    def __repr__(self) -> str:
        return str(self)


class Storage:
    def __init__(self, init=dict()) -> None:
        self.data = init

    def get(self, slot):
        if not is_valid_uint256(slot):
            raise InvalidStorageSlot(slot)
        return self.data.get(slot, 0)

    def put(self, slot, value):
        if not is_valid_uint256(slot):
            raise InvalidStorageSlot(slot)

        if not is_valid_uint256(value):
            raise InvalidStorageValue(value)

        self.data[slot] = value


class AccountState:
    def __init__(self, nonce=0, balance=0, storage=None, code=bytes()) -> None:
        self.nonce = nonce
        self.balance = balance
        self.storage = storage if storage else Storage()
        self.code = code

    def is_empty(self):
        return self.nonce == 0 and self.balance == 0 and self.code == b""

    def __str__(self):
        return f"nonce: {self.nonce}, balance: {self.balance}, code: {self.code}, storage: {self.storage}"


class WorldState:
    def __init__(self, accounts=dict()) -> None:
        self.accounts = accounts

    def get(self, address):
        return self.accounts[address]

    def set(self, address, account):
        self.accounts[address] = account

    def __str__(self):
        return str(self.accounts)

    def __repr__(self):
        return str(self)
