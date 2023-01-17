#!/usr/bin/env python3
import json
import os

from smol_evm.runner import run

# run with
# $ poetry run ./examples/w1nt3r-runner.py

# see https://github.com/w1nt3r-eth/evm-from-scratch


def evm(code):
    context = run(code=code)
    # get the backing list
    stack = context.stack.stack
    # reverse it to follow the convention of the test cases
    stack.reverse()
    return stack


def error(test: dict, num: int, msg: str):
    print(f"❌ Test #{num} {test['name']}")

    print(msg)

    print("\nTest code:")
    print(test["code"]["asm"])

    print("\nHint:", test["hint"])


def test():
    script_dirname = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dirname, "w1nt3r-evm-from-scratch", "evm.json")
    with open(json_file) as f:
        data = json.load(f)
        total = len(data)

        print(f"Running {total} tests...")

        for i, test in enumerate(data):
            # Note: as the test cases get more complex, you'll need to modify this
            # to pass down more arguments to the evm function
            code = bytes.fromhex(test["code"]["bin"])
            expected_stack = [int(x, 16) for x in test["expect"]["stack"]]

            try:
                stack = evm(code)
            except Exception as e:
                error(
                    test,
                    i + 1,
                    f"expected stack: {expected_stack}\nbut execution raised: {e}",
                )

                print("\nTrace:")
                run(code=code, verbose=True, print_stack=True, print_memory=True)

                break

            # if any value differs:
            if any(x != y for x, y in zip(stack, expected_stack)):
                error(
                    test,
                    i + 1,
                    f"Stack doesn't match\n expected: {expected_stack}\n   actual: {stack}",
                )

                print("\nTrace:")
                run(code=code, verbose=True, print_stack=True, print_memory=True)

                break

            else:
                print(f"✅ Test #{i + 1} {test['name']}")


if __name__ == "__main__":
    test()
