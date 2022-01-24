from .context import ExecutionContext


def run(code: bytes, context=ExecutionContext()) -> None:
    """
    Execute the code in the given context.
    """

    # TODO: underflows and overflows
    # TODO: gas cost
    while not context.stopped:
        opcode = code[context.pc]
        context.pc += 1
        if opcode == 0x00:
            # STOP
            context.stopped = True

        elif opcode == 0x01:
            # ADD
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(a + b)

        elif opcode == 0x02:
            # MUL
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(a * b)

        elif opcode == 0x03:
            # SUB
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(b - a)

        elif opcode == 0x04:
            # DIV
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(b // a)

        elif opcode == 0x05:
            # SDIV
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(b // a)

        elif opcode == 0x06:
            # MOD
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(b % a)

        elif opcode == 0x07:
            # SMOD
            a = context.stack.pop()
            b = context.stack.pop()
            context.stack.push(b % a)

        elif opcode == 0x08:
            # ADDMOD
            a = context.stack.pop()
            b = context.stack.pop()
            c = context.stack.pop()
            context.stack.push((b + a) % c)

        elif opcode == 0x09:
            # MULMOD
            a = context.stack.pop()
            b = context.stack.pop()
            c = context.stack.pop()
            context.stack.push((b * a) % c)

        elif opcode == 0x60:
            # PUSH1
            value = code[context.pc]
            context.stack.push(value)
            context.pc += 1

        else:
            raise Exception("Invalid opcode " + str(opcode))

        # TODO: if DEBUG
        print(context)
