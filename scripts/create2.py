#!/usr/bin/env python3

from multiprocessing import Pool, Event
from web3 import Web3

import os
import random
import sys


def init_pool_processes(the_shutdown_event):
    """
    Initialize each process with the global shutdown event
    """
    global shutdown_event
    shutdown_event = the_shutdown_event


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


class Create2Searcher:
    def __init__(self, deployer_addr, predicate_str, bytecode):
        self.deployer_addr = deployer_addr
        self.predicate_str = predicate_str
        self.hashed_bytecode = Web3.toHex(Web3.keccak(hexstr=bytecode))[2:]

    def search(self, starting_salt=0):
        predicate = eval(self.predicate_str)
        salt = starting_salt
        print("Starting search with salt:", hex(salt)[2:].zfill(64))
        while True:
            salt_hexstr = hex(salt)[2:].zfill(64)
            addr = _create2(self.deployer_addr, salt_hexstr, self.hashed_bytecode)
            salt += 1

            if predicate(addr):
                print(
                    f"\nFound a match! Deploying with salt={salt} to get address {addr}"
                )
                shutdown_event.set()

            if (salt % 10000) == 0 and shutdown_event.is_set():
                print(f"Stopped searching after {salt - starting_salt} attempts")
                break


def main():
    if len(sys.argv) != 4:
        print(
            f"""Usage: python3 {sys.argv[0]} deployer_addr <salt | predicate> bytecode

When passing a salt value, this script prints the address of the newly deployed contract based on the deployer address and bytecode hash.
Example: python3 {sys.argv[0]} Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 42 602a60205260206020f3

When passing a predicate, this script will search for a salt value such that the new address satisfies the predicate.
Example: python3 {sys.argv[0]} Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 'lambda addr: \"badc0de\" in addr.lower()' 602a60205260206020f3

Another predicate that may be useful: 'lambda addr: addr.startswith(\"0\" * 8)'
"""
        )
        sys.exit(0)

    deployer_addr = sys.argv[1]
    if deployer_addr.startswith("0x"):
        deployer_addr = deployer_addr[2:]

    bytecode = sys.argv[3]

    try:
        salt = int(sys.argv[2])
        print(create2(deployer_addr, salt, bytecode))
        sys.exit(0)
    except ValueError:
        pass

    predicate_str = sys.argv[2]
    process_count = os.cpu_count()

    print(f"👷‍♂️ Starting {process_count} worker processes")
    shutdown_event = Event()
    searcher = Create2Searcher(deployer_addr, predicate_str, bytecode)

    with Pool(
        processes=process_count,
        initializer=init_pool_processes,
        initargs=(shutdown_event,),
    ) as pool:
        pool.map(searcher.search, [2 ** 64 * x for x in range(os.cpu_count())])
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
