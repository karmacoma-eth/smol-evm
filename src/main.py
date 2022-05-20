#!/usr/bin/env python3

from smol_evm.runner import run

import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: {} <hexdata>".format(sys.argv[0]))
        sys.exit(1)

    data = sys.argv[1]
    ret = run(bytes.fromhex(data), verbose=True)
    print(f"0x{ret.hex()}")


if __name__ == "__main__":
    main()
