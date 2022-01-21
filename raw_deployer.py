import string
import sys


def bin2(value):
    return binN(value, 2)

def bin4(value):
    return binN(value, 4)

def binN(value, N):
    assert N % 2 == 0
    return "{:x}".format(value).zfill(N)


class Instruction:
    def __init__(self, opcode, arg_length=None, arg=None):
        self.opcode = opcode
        self.arg_length = arg_length
        self.arg = arg

    def to_bin(self):
        if self.arg is None:
            return bin2(self.opcode)

        return bin2(self.opcode) + binN(self.arg, 2 * self.arg_length)


class Block:
    def __init__(self, instructions):
        self.instructions = instructions

    def to_bin(self):
        return ''.join([x.to_bin() for x in self.instructions])


def PUSH1(arg):
    return Instruction(0x60, 1, arg)

def PUSH2(arg):
    return Instruction(0x61, 2, arg)

DUP1 = Instruction(0x80)
CODECOPY = Instruction(0x39)
RETURN = Instruction(0xf3)
INVALID = Instruction(0xfe)


def main():
    runtime_bin = sys.argv[1]
    assert len(runtime_bin) % 2 == 0
    assert all([x in string.hexdigits for x in runtime_bin])

    # in bytes
    runtime_bin_length = len(runtime_bin) // 2

    # PUSH2 ought to be enough for anybody
    push_length = PUSH1(runtime_bin_length) if runtime_bin_length <= 0xff else PUSH2(runtime_bin_length)

    # we need to see how long the init code is first and then we can backfill this
    push_offset = PUSH1(0)

    initcode = Block([
        push_length,
        DUP1,
        push_offset,
        PUSH1(0), # mem destination
        CODECOPY, # copies code[runtime_bin_offset .. offset + runtime_bin_length] to mem[0]
        PUSH1(0),
        RETURN,   # returns mem[0 .. runtime_bin_length]
        INVALID   # not stricly necessary, but makes it easier to find the end
    ])

    # since runtime_bin will come right after the init code, runtime_bin_offset is just the init code length
    initcode_length = len(initcode.to_bin()) // 2
    push_offset.arg = initcode_length

    print(initcode.to_bin() + runtime_bin)


if __name__ == "__main__":
    main()
