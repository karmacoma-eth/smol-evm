#!/usr/bin/env python3

import json
import os
import sys
import time

from web3 import Web3
from web3._utils.events import get_event_data

# based on https://ethereum.stackexchange.com/questions/106868/listen-to-events-in-the-polygon-network-using-web3-py

# might start getting timeouts if this gets too big
BLOCK_RANGE_SIZE = 1000

ETH_RPC_URL = os.environ.get('ETH_RPC_URL', 'http://localhost:8545')
print('ETH_RPC_URL:', ETH_RPC_URL)
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

def handle_event(event, event_template):
    try:
        result = get_event_data(event_template.web3.codec, event_template._get_event_abi(), event)
        return True, result
    except:
        return False, None


def main():
    address, abi_json_filename, event_name, from_block = sys.argv[1:]
    from_block = int(from_block)
    print(f'Starting from block {from_block} with block range size {BLOCK_RANGE_SIZE}')

    with open(abi_json_filename) as f:
        abi = json.load(f)['abi']

    contract = w3.eth.contract(address=address, abi=abi)
    event_template = contract.events[event_name]

    earliest_block = from_block
    latest_block = w3.eth.get_block_number()

    while from_block < latest_block:
        done = from_block - earliest_block
        print(f'from_block: {from_block} ({done / (latest_block - earliest_block) * 100:.2f}%)')

        to_block = from_block + BLOCK_RANGE_SIZE
        events = w3.eth.get_logs(
            {
                'fromBlock': from_block,
                'toBlock': to_block,
                'address': address
            }
        )
        from_block = to_block

        for event in events:
            suc, res = handle_event(event=event, event_template=event_template)
            if suc:
                print("Event found", res)

        time.sleep(1)


if __name__ == '__main__':
    main()