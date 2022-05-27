#!/usr/bin/env python3

import random
import sys
from web3 import Web3


def _create2(deployer, salt_hexstr, hashed_bytecode):
    addr_hexbytes = Web3.keccak(
        hexstr=("ff" + deployer + salt_hexstr + hashed_bytecode)
    )
    addr = Web3.toHex(addr_hexbytes)[-40:]
    return addr


# expecting deployer='aabbccdd' (20 bytes -> 40 characters)
# salt = some decimal number
# bytecode = 'aabbccddeeff...' (variable length)
def create2(deployer, salt, bytecode):
    assert len(deployer) == 40
    assert len(bytecode) % 2 == 0
    salt_hexstr = hex(salt)[2:].zfill(64)
    hashed_bytecode = Web3.toHex(Web3.keccak(hexstr=bytecode))[2:]
    return _create2(deployer, salt_hexstr, hashed_bytecode)


def create2_search(deployer, predicate, bytecode):
    salt = 0
    hashed_bytecode = Web3.toHex(Web3.keccak(hexstr=bytecode))[2:]
    while True:
        salt += 1
        salt_hexstr = hex(salt)[2:].zfill(64)
        addr = _create2(deployer, salt_hexstr, hashed_bytecode)
        if salt % 1000 == 0:
            print(".", end="", flush=True)

        if predicate(addr):
            print(f"\nFound a match after {salt} attempts: {addr}")
            break


def main():
    if len(sys.argv) != 4:
        print(f"Usage: python3 {sys.argv[0]} deployer_addr <salt | predicate> bytecode")
        print()
        print(
            f"When passing a salt value, this script prints the address of the newly deployed contract based on the deployer address and bytecode hash."
        )
        print(
            f"Example: python3 {sys.argv[0]} Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 42 602a60205260206020f3"
        )
        print()
        print(
            f"When passing a predicate, this script will search for a salt value such that the new address satisfies the predicate."
        )
        print(
            f"Example: python3 {sys.argv[0]} Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 'lambda addr: \"badc0de\" in addr.lower()' 602a60205260206020f3"
        )
        print(
            f"Another predicate that may be useful: 'lambda addr: addr.startswith(\"0\" * 8)' 602a60205260206020f3"
        )
        sys.exit(0)

    deployer_addr = sys.argv[1]
    if deployer_addr.startswith("0x"):
        deployer_addr = deployer_addr[2:]

    bytecode = sys.argv[3]

    try:
        salt = int(sys.argv[2])
        print(create2(deployer_addr, salt, bytecode))
    except ValueError:
        predicate = eval(sys.argv[2])
        create2_search(deployer_addr, predicate, bytecode)


if __name__ == "__main__":
    main()
