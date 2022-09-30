#!/usr/bin/env python3

import argparse

from smol_evm.context import Calldata
from smol_evm.opcodes import UnknownOpcode
from smol_evm.runner import run


def strip_0x(s: str):
    return s[2:] if s and s.startswith("0x") else s


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

    try:
        ret = run(
            code=code,
            calldata=calldata,
            verbose=True,
            print_stack=True,
            print_memory=True,
        )
        print(f"0x{ret.hex()}")
    except UnknownOpcode as e:
        print(f"🚧 Encountered an unknown/unimplemented opcode: {hex(e.opcode)}")
        print(f"If you want to contribute to smol🤏evm, now is your chance!")
        print()
        print(f"    🕵️‍♂️  Look up the opcode: https://ethereum.github.io/yellowpaper")
        print(f"    🧰 Implement it in src/smol_evm/opcodes.py")
        print(f"    👨‍💻 Create some unit tests for it")
        print(f"    💣 Run the tests: `poetry run pytest -v`")
        print(f"    🏗️  Create a pull request on GitHub")
        print(f"    🥳 Congrats, you're a contributor!")
        print()


if __name__ == "__main__":
    main()
