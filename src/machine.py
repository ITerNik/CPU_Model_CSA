import json
import logging
import sys

from isa import MachineCode, Code


def main(code_file, input_file):
    with open(code_file, encoding="utf-8") as file:
        code = json.loads(file.read())
        machine_code = MachineCode(list(map(lambda d: Code(**d), code['code'])), code['data'])
    with open(input_file,  encoding="utf-8") as file:
        input_text = sorted(json.loads(file.read()))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
