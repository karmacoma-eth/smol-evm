#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from web3 import Web3

# from https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


logging.basicConfig(level=logging.WARN)

ETH_RPC_URL = os.environ.get("ETH_RPC_URL", "http://localhost:8545")
logging.debug(f"ETH_RPC_URL: {ETH_RPC_URL}")
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))


def process_block(addr, block_id="latest"):
    matches = []

    block = w3.eth.get_block(block_id, full_transactions=True)
    for tx in block.transactions:
        logging.debug(tx)

        # to is None for contract creation
        to_addr = tx.to or "0x"

        if tx["from"].lower() == addr or to_addr.lower() == addr:
            logging.debug(tx["input"])
            matches.append(tx)

    return block.number, matches


def render(transactions):
    for tx in transactions:
        text = Web3.toText(tx["input"])
        if text:
            print(f"{bcolors.OKGREEN}{Web3.toHex(tx.hash)}{bcolors.ENDC}")
            print(f"{text}\n")


def main():
    parser = argparse.ArgumentParser(description="Parse calldata as UTF-8 messages")
    parser.add_argument("--addr", help="address to watch", required=True)
    parser.add_argument(
        "--starting-block", help="start looking for transactions at this block number"
    )

    args = parser.parse_args()
    logging.debug(args)

    if args.starting_block is None:
        block_number, matches = process_block(args.addr)
        if not matches:
            print(f"No match found in block number {block_number}")
        else:
            render(matches)

    else:
        block_number = int(args.starting_block)
        while block_number < w3.eth.get_block_number():
            block_number, matches = process_block(args.addr, block_number)
            render(matches)
            block_number += 1


if __name__ == "__main__":
    main()
