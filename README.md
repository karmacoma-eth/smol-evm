# smol-evm

👨‍🔬 An extensible Python implementation of the Ethereum yellow paper from scratch.

Write-up with examples:

[Building an EVM from scratch](https://karmacoma.notion.site/Building-an-EVM-from-scratch-series-90ee3c827b314e0599e705a1152eecf9) [karmacoma.notion.so]

# Getting started

Install smol-evm in [a virtual environment](https://realpython.com/python-virtual-environments-a-primer/)

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ python -m pip install smol-evm
```

Run the CLI:

```
$ smol-evm --help
Usage: smol-evm [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help                Show this message and exit.

Commands:
  disassemble  Disassembles the given bytecode
  run          Creates an EVM execution context and runs the given bytecode

$ smol-evm run
````

Execute bytecode:

```bash
$ smol-evm run --code 602a6000526001601ff3 --no-trace
0x2a
```

Disassemble bytecode:

```bash
$ smol-evm disassemble --code 602a6000526001601ff3
0000: PUSH1 0x2a
0002: PUSH1 0x00
0004: MSTORE
0005: PUSH1 0x01
0007: PUSH1 0x1f
0009: RETURN
```

Assemble bytecode:

```bash
smol-evm disassemble --code 602a6000526001601ff3 | smol-evm assemble -
602a6000526001601ff3
```

Use as a library:

```bash
python
>>> from smol_evm.opcodes import *
>>> code = assemble([PC, DUP1, MSTORE])
588052
```

⚠️ _please note that the interface is very much not stable and is subject to frequent changes_

# Developer mode

> Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

> Install Dependencies

```bash
poetry install
```

> Run Tests

```bash
poetry run pytest -v
```

> Run the `black` code formatter

```bash
poetry run black src
```

# Misc scripts

## raw_deployer.py

Takes the binary representation of a contract and generates the init code that will deploy that contract (Ti in Yellow Paper terminology).

For instance, let's say that you have some Yul code, that when compiled with `solc` has the following binary representation: `602a60205260206020f3`.

```
> python raw_deployer.py 602a60205260206020f3
600a8061000d6000396000f3fe602a60205260206020f3
```

You can now deploy this code:

```javascript
web3.eth.sendTransaction({
    from: /* your address */,
    /* no to address as we are creating a contract */
    data: "600a8061000d6000396000f3fe602a60205260206020f3"
})
```

Wait for the transaction to be confirmed, and go look at the code of the contract that was deployed, it should match our compiled Yul code `602a60205260206020f3` 🙌


## create2.py
Based on web3.py, this script can find addresses of contracts deployed by the `CREATE2` opcode that satisfy a particular predicate.

Usage: `python3 create2.py deployer_addr <salt | predicate> bytecode`

When passing a salt value, this script prints the address of the newly deployed contract based on the deployer address and bytecode hash.

Example: `python3 create2.py Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 42 602a60205260206020f3`

When passing a predicate, this script will search for a salt value such that the new address satisfies the predicate.

Example: `python3 create2.py Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 'lambda addr: "badc0de" in addr.lower()' 602a60205260206020f3`

Another predicate that may be useful: `'lambda addr: addr.startswith("0" * 8)'`

Use with a deployer contract like this:

```solidity
contract Deployer {
    function deploy(bytes memory code, uint256 salt) public returns(address) {
        address addr;
        assembly {
          addr := create2(0, add(code, 0x20), mload(code), salt)
          if iszero(extcodesize(addr)) {
            revert(0, 0)
          }
        }

        return addr;
    }
}
```
