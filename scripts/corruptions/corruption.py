from collections import defaultdict
from time import sleep
from web3 import Web3

import requests


CORRUPTIONS_CONTRACT_ADDRESS = '0x5bdf397bb2912859dbd8011f320a222f79a28d2e'

phrases = [
    "GENERATION",
    "INDIVIDUAL",
    "TECHNOLOGY",
    "EVERYTHING",
    "EVERYWHERE",
    "UNDERWORLD",
    "ILLUMINATI",
    "TEMPTATION",
    "REVELATION",
    "CORRUPTION"
]

borders_and_corruptors = [
    "/",
    "$",
    "|",
    "8",
    "_",
    "?",
    "#",
    "%",
    "^",
    "~",
    ":",
]

checkers = [
    "|",
    "-",
    "=",
    "+",
    "\\",
    ":",
    "~"
]

bgcolors = [
    "#022FB7",
    "#262A36",
    "#A802B7",
    "#3CB702",
    "#B76F02",
    "#B70284",
]

# actually unused
fgcolors  = [
    "#0D1302",
    "#020A13",
    "#130202",
    "#1A1616",
    "#000000",
    "#040A27",
]


class Corruption:
    """
    Each Corruption models one token and its properties.

    >>> token_0 = Corruption(0)
    >>> token_0.get_token_id()
    0
    >>> token_0.get_phrase()
    'CORRUPTION'
    >>> token_0.get_border()
    '$'
    >>> token_0.get_corruptor()
    '8'
    >>> token_0.get_bgcolor()
    '#B70284'
    >>> token_0.get_secret_phrase()
    'EVERYWHERE'
    >>> token_0.get_checker()
    '='
    """

    def __init__(self, tokenId):
        self.tokenId = tokenId

    def get_token_id(self):
        return self.tokenId

    def get_phrase(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["PHRASE", self.tokenId])
        return phrases[Web3.toInt(hash) % 10]

    def get_num_iterations(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["CORRUPTION", self.tokenId])
        return Web3.toInt(hash) % 1024

    def get_border(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["BORDER", self.tokenId])
        return borders_and_corruptors[Web3.toInt(hash) % 11]

    def get_corruptor(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["CORRUPTOR", self.tokenId])
        return borders_and_corruptors[Web3.toInt(hash) % 11]

    def get_bgcolor(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["BGCOLOR", self.tokenId])
        return bgcolors[Web3.toInt(hash) % 6]

    def get_secret_phrase(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["FGCOLOR", self.tokenId])
        return phrases[len(phrases) - 6 + Web3.toInt(hash) % 6]

    def get_checker(self):
        hash = Web3.solidityKeccak(['string', 'uint256'], ["CHECKER", self.tokenId])
        return checkers[Web3.toInt(hash) % 7]

    def get_orders(self):
        url = "https://api.opensea.io/wyvern/v1/orders?bundled=false&include_bundled=false&include_invalid=false&limit=20&offset=0&order_by=created_date&order_direction=desc"

        url += f"&side=1" # only sell orders
        url += f"&asset_contract_address={CORRUPTIONS_CONTRACT_ADDRESS}"
        url += f"&token_id={self.tokenId}"

        response = requests.request("GET", url, headers={"Accept": "application/json"})
        return response.json()


    def __str__(self):
        return f"{self.get_token_id()}\t{self.get_phrase()}\t{self.get_secret_phrase()}\t{self.get_border()}\t{self.get_corruptor()}\t{self.get_checker()}\t{self.get_bgcolor()}\t{self.get_num_iterations()}"


# all the tokens:
corruptions = [Corruption(i) for i in range(4196)]


###############################################################################
# CONVENIENCE FUNCTIONS
# these output tab-separated values, for easy pasting in Google sheets
# and command line filtering

def get_iterations():
    for c in corruptions:
        print(c.get_token_id(), '\t', c.get_num_iterations())


def get_phrases():
    for c in corruptions:
        print(c.get_token_id(), '\t', c.get_phrase())


def get_secret_phrases():
    for c in corruptions:
        print(c.get_token_id(), '\t', c.get_secret_phrase())


def get_borders():
    for c in corruptions:
        print(c.get_token_id(), '\t', c.get_border())


def get_backgrounds():
    bgcolors = defaultdict(int)

    for c in corruptions:
        bgcolors[c.get_bgcolor()] += 1

    for color, count in sorted(bgcolors.items(), key=lambda x: x[1], reverse=True):
        print(f"console.log('{count} %c    ', 'background: {color};');")


def get_corruptors():
    for c in corruptions:
        print(c.get_token_id(), '\t', c.get_corruptor())


def get_tokens_with_same_border_and_corruptor():
    same = [(x.get_token_id(), x.get_corruptor()) for x in corruptions if x.get_border() == x.get_corruptor()]
    for (token_id, corruptor) in same:
        print(token_id, '\t', corruptor)


def get_tokens_with_same_phrase_and_secret_phrase():
    same = [(x.get_token_id(), x.get_phrase()) for x in corruptions if x.get_phrase() == x.get_secret_phrase()]
    for (token_id, phrase) in same:
        print(token_id, '\t', phrase)


def get_triple_perfect_corruptions():
    return [x for x in corruptions if x.get_phrase() == x.get_secret_phrase() and x.get_corruptor() == x.get_border() and x.get_corruptor() == x.get_checker()]


def get_corruptor_and_checker_perfects():
    return [x for x in corruptions if x.get_phrase() == x.get_secret_phrase() and x.get_corruptor() == x.get_checker()]



def print_collection(some_corruptions):
    for c in some_corruptions:
        print(c)


def fetch_prices(some_corruptions):
    for perfect_token in some_corruptions:
        print(f'fetching sell orders for token_id {perfect_token.get_token_id()}...\t', end='')
        orders = perfect_token.get_orders()['orders']

        # {'count': 1, 'orders': []}
        if len(orders) > 0:
            order = orders[0]
            price = float(order['current_price']) / 10 ** int(order['payment_token_contract']['decimals'])
            print(f"{price} {order['payment_token_contract']['symbol']}")

        else:
            print ('not for sale')

        sleep(1)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    collection = get_corruptor_and_checker_perfects()
    print_collection(collection)
    fetch_prices(collection)