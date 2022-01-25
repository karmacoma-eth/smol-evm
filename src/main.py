#!/usr/bin/env python3

from yolo_evm.runner import run

import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: {} <hexdata>".format(sys.argv[0]))
        sys.exit(1)

    data = sys.argv[1]
    run(bytes.fromhex(data))


if __name__ == "__main__":
    main()
