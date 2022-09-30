## How to contribute code to smol🤏evm

If you want to contribute an instruction that has not been implemented yet:

1. look up the opcode's behavior in the [yellow paper](https://ethereum.github.io/yellowpaper)
1. build some intuition with [evm.codes](https://www.evm.codes/)
1. clone this repository, create a new branch
1. implement the missing instruction in [opcodes.py](https://github.com/karmacoma-eth/smol-evm/blob/main/src/smol_evm/opcodes.py)
1. write some unit tests, ideally checking for both happy cases and weird/extreme values, overflows, etc
1. make sure the tests pass: `poetry run pytest -v`
1. open a pull request!
1. ping [karma](https://twitter.com/0xkarmacoma) if you don't hear back reasonably fast

If you need some inspiration, check out [this commit](https://github.com/karmacoma-eth/smol-evm/commit/7f2d2977a563f6d94ea6bb19408fbf94b1d13ab5) that implements a handful of instructions and the corresponding tests.

