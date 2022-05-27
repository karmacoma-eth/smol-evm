#!/usr/bin/env python3

import argparse
import os
import subprocess

from functools import partial

from smol_evm.context import ExecutionContext
from smol_evm.opcodes import Instruction, EQ, LT, GT
from smol_evm.runner import run

DEBUG = False


def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")


def strip_0x(s: str):
    if s and s.startswith("0x"):
        return s[2:]


class Tracer:
    def __init__(self, sentinel: int):
        self.sentinel = sentinel
        self.eq = []
        self.lt = []
        self.gt = []

    def prehook(self, context: ExecutionContext, instruction: Instruction):
        if instruction not in (EQ, LT, GT):
            return

        s0, s1 = context.stack.peek(0), context.stack.peek(1)
        other = None
        if self.sentinel == s0:
            debug(f"test for sentinel {instruction} {hex(s1)}")
            other = s1
            if instruction is LT:
                self.gt.append(other) if self.sentinel < s1 else self.lt.append(other)
            elif instruction is GT:
                self.lt.append(other) if self.sentinel > s1 else self.gt.append(other)

        elif self.sentinel == s1:
            debug(f"test for {hex(s0)} {instruction} sentinel")
            other = s0
            if instruction is LT:
                self.lt.append(other) if s0 < self.sentinel else self.gt.append(other)
            elif instruction is GT:
                self.gt.append(other) if s0 > self.sentinel else self.lt.append(other)

        else:
            debug(
                f"test for {hex(s0)} {instruction} {hex(s1)} does not match the sentinel value {hex(self.sentinel)}"
            )

        if instruction is EQ and other is not None:
            self.eq.append(other)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--code",
        help="hex data of the code to run, e.g. using `cast code <deployment_addr>`",
        required=True,
    )
    args = parser.parse_args()

    code = bytes.fromhex(strip_0x(args.code))

    lt = set([0xAABBCCDE])
    gt = set()
    eq = set()
    done = set()
    iteration = 0

    while True:
        # pick a sentinel
        if len(lt) > 0:
            sentinel = lt.pop() - 1
        elif len(gt) > 0:
            sentinel = gt.pop() + 1
        else:
            break

        if sentinel in done:
            continue

        done.add(sentinel)

        # run again with the new sentinel, and trace the results
        iteration += 1
        print(f"Iteration {iteration} with sentinel {hex(sentinel)}")
        tracer = Tracer(sentinel)
        try:
            run(
                code=code,
                calldata=bytes.fromhex(hex(sentinel)[2:]),
                verbose=False,
                prehook=partial(Tracer.prehook, tracer),
            )
        except Exception as e:
            debug(f"ignoring exception {type(e)}: {e}")

        lt = lt.union(tracer.lt)
        gt = gt.union(tracer.gt)
        eq = eq.union(tracer.eq)

    selectors = ("0x" + hex(x)[2:].zfill(8) for x in eq)
    print(f"Found {len(eq)} potential selectors in {iteration} iterations")

    for selector in selectors:
        debug(f"+ cast 4byte {selector}")

        cast = subprocess.run(f"cast 4byte {selector}".split(), stdout=subprocess.PIPE)
        print(f"{selector}:")
        for line in cast.stdout.decode().splitlines():
            print(f"  - {line}")
        print()


if __name__ == "__main__":
    main()
