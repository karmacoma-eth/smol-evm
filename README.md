# yolo-evm

A random collection of hacky scripts related to EVM development and challenges.

# Installation

> Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

> Run Tests

```bash
poetry run pytest -v
```

> Run the `black` code formatter

```bash
poetry run black src
```

# Random scripts

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

### Deployer addresses

- Goerli: `0x986D6f3137d22FE771308E383ef63af9B4Af2CCE`
- Ropsten: `0x9c5408C256E04432a75Ea7e8EC7918DA8E578222`
- Kovan: `0x44817A86dF91Decf2c8164e357ad6bF069EeC77D`
- Rinkeby: `0x44817A86dF91Decf2c8164e357ad6bF069EeC77D`