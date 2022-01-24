#!/usr/bin/env python3

from yolo_evm.runner import run

import sys

def main():
    if len(sys.argv) != 2:
        print('Usage: {} <hexdata>'.format(sys.argv[0]))
        sys.exit(1)

    data = sys.argv[1]

    as_bytes = bytes([int(data[2*i:2*(i+1)], 16) for i in range(0, len(data) // 2)])
    print('executing', as_bytes)
    run(as_bytes)

if __name__ == '__main__':
    main()

