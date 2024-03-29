import click
import os

import smol_evm.runner
import smol_evm.opcodes
import disasm

from smol_evm.utils import strip_0x


def load_bytecode(code: str) -> bytes:
    """Load bytecode from a file or a hex string"""
    if os.path.exists(code):
        with open(code, "r") as f:
            return bytes.fromhex(strip_0x(f.read()))

    else:
        return bytes.fromhex(strip_0x(code))


@click.group()
# @click.option("--debug/--no-debug", default=False)
def cli():
    # TODO: set logging level
    pass


@cli.command()
@click.option("--code", help="bytecode as hex string, e.g. 6080604052", required=True)
@click.option("--calldata", help="hex data to use as transaction input, e.g. cfae3217")
@click.option("--trace/--no-trace", help="print the full instruction trace", default=True)
@click.option("--stack/--no-stack", help="enables stack output in the trace", default=False)
@click.option("--memory/--no-memory", help="enables memory output in the trace", default=False)
def run(code: str, calldata: str, trace: bool, stack: bool, memory: bool):
    """Execute bytecode"""
    code_bytes = load_bytecode(code)
    calldata_bytes = bytes.fromhex(strip_0x(calldata)) if calldata else bytes()

    ret = smol_evm.runner.run(
        code=code_bytes,
        calldata=calldata_bytes,
        verbose=trace,
        print_stack=stack,
        print_memory=memory,
    ).returndata

    click.echo(f"0x{ret.hex()}")


@cli.command()
@click.option("--code", help="bytecode as hex string, e.g. 6080604052", required=True)
def disassemble(code: str):
    """Turn bytecode into assembly code"""
    code_bytes = load_bytecode(code)
    click.echo("\n".join(disasm.disassemble(code_bytes)))


@cli.command()
@click.argument('input_file', type=click.File('r'))
def assemble(input_file):
    """Turn assembly code into bytecode"""
    smol_evm.opcodes.assemble(input_file.readlines(), print_bin=True)
