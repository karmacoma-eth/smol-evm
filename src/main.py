#!/usr/bin/env python3

import argparse

from smol_evm.context import Calldata
from smol_evm.runner import run


def strip_0x(s: str):
    if s and s.startswith("0x"):
        return s[2:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", help="hex data of the code to run", required=True)
    parser.add_argument(
        "--calldata",
        help="hex data to use as input, e.g. 0xcfae3217",
    )
    args = parser.parse_args()

    code = bytes.fromhex(strip_0x(args.code))
    calldata = bytes.fromhex(strip_0x(args.calldata)) if args.calldata else bytes()

    ret = run(code=code, calldata=calldata, verbose=True)
    print(f"0x{ret.hex()}")


if __name__ == "__main__":
    main()
