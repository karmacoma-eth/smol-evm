#!/usr/bin/env python3
import json
import os

from smol_evm.runner import run


def evm(code):
    context = run(code=code)
    # get the backing list
    stack = context.stack.stack
    # reverse it to follow the convention of the test cases
    stack.reverse()
    return stack


def test():
    script_dirname = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dirname, "w1nt3r-evm-from-scratch", "evm.json")
    with open(json_file) as f:
        data = json.load(f)
        total = len(data)

        for i, test in enumerate(data):
            # Note: as the test cases get more complex, you'll need to modify this
            # to pass down more arguments to the evm function
            code = bytes.fromhex(test["code"]["bin"])

            stack = evm(code)

            expected_stack = [int(x, 16) for x in test["expect"]["stack"]]

            # if any value differs:
            if any(x != y for x, y in zip(stack, expected_stack)):
                print(f"❌ Test #{i + 1}/{total} {test['name']}")

                print("Stack doesn't match")
                print(" expected:", expected_stack)
                print("   actual:", stack)
                print("")
                print("Test code:")
                print(test["code"]["asm"])
                print("")
                print(f"Progress: {i}/{len(data)}")
                print("")

                print("Trace:")
                run(code=code, verbose=True, print_stack=True, print_memory=True)

                break

            else:
                print(f"✅ Test #{i + 1}/{total} {test['name']}")


if __name__ == "__main__":
    test()
