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
  --help  Show this message and exit.

Commands:
  assemble     Turn assembly code into bytecode
  disassemble  Turn bytecode into assembly code
  run          Execute bytecode
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

Using smol-evm programmatically lets you do things like [memhook.py](https://github.com/karmacoma-eth/smol-evm/blob/main/examples/memhook.py):

```python
"""This example shows how to hook and hijack memory writes"""

from smol_evm.opcodes import *
from smol_evm.runner import run

def prehook(context, instruction):
    if instruction.opcode == MSTORE.opcode:
        offset, expected = context.stack.pop(), context.stack.pop()
        context.stack.push(0xdeadbeef)
        context.stack.push(offset)

code = assemble([
    PUSH(0x42),
    PUSH(0),
    MSTORE,
    PUSH(0x20),
    PUSH(0),
    RETURN,
], print_bin=False)

print("unmodified return value:", run(code, verbose=False).returndata.hex())
print("hijacked return value:", run(code, verbose=False, prehook=prehook).returndata.hex())
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

