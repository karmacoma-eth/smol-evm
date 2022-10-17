import os
import tomlkit
import subprocess
import sys

from main import with_args, Args


def is_huff_installed():
    try:
        ret = subprocess.run(["huffc", "--version"], check=True)
        if ret.returncode != 0:
            print("WARN: huffc --version returned non-zero exit code")
        return True
    except FileNotFoundError:
        return False


def runtime_bytecode(huff_file):
    p = subprocess.Popen(["huffc", huff_file, "--bin-runtime"], stdout=subprocess.PIPE)
    returncode = p.wait()
    # TODO: handle returncode != 0
    return p.stdout.read().decode("utf-8").strip()


def toml_parse(toml_file):
    with open(toml_file) as f:
        return tomlkit.parse(f.read())


def run_huff(huff_file):
    dirname = os.path.dirname(huff_file)
    basename = os.path.basename(huff_file)

    toml_file = os.path.join(dirname, basename.replace(".huff", ".toml"))
    toml = toml_parse(toml_file)

    code = runtime_bytecode(huff_file)

    for test_name, test_config in toml.items():
        calldata = test_config["calldata"]

        ret = with_args(
            Args(code, calldata, verbose=False, print_stack=False, print_memory=False)
        )
        ret_hex = f"0x{ret.hex()}"

        # if any test config has an 'expected-<field>' key, compare the result
        if any(k.startswith("expected-") for k in test_config.keys()):
            # TODO: handle other expected fields
            expected_returndata = test_config["expected-returndata"]
            if ret_hex == expected_returndata:
                print(f"✅ {test_name}")

            else:
                print(f"❌ {test_name}")
                print(f"expected: {expected_returndata}")
                print(f"  actual: {ret_hex}")

        else:
            print(f"🤖 {test_name}")
            print(f"{ret_hex}")


def main():
    if not is_huff_installed():
        print("ERROR: huffc not found in PATH")
        sys.exit(1)

    # TODO: proper arg parsing
    huff_file = sys.argv[1]
    run_huff(huff_file)


if __name__ == "__main__":
    main()
