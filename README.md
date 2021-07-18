# yolo-evm

A random collection of hacky scripts related to EVM development and challenges.

## raw_deployer.py

Takes the binary representation of a contract and generates the init code that will deploy that contract (Ti in Yellow Paper terminology).

For instance, let's say that you have some Yul code, that when compiled with `solc` has the following binary representation: `602a60205260206020f3`.

```
> python raw_deployer.py 602a60205260206020f3
600a8061000d6000396000f3fe602a60205260206020f3
```

You can now deploy this code:

```
web3.eth.sendTransaction({
    from: /* your address */, 
    /* no to address as we are creating a contract */ 
    data: "600a8061000d6000396000f3fe602a60205260206020f3"
})
```

Wait for the transaction to be confirmed, and go look at the code of the contract that was deployed, it should match our compiled Yul code `602a60205260206020f3` 🙌

