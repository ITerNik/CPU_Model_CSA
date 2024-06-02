from __future__ import annotations

import json
import sys

from isa import Addressing, Code, MachineCode, MachineCodeEncoder, Opcode


# flake8: noqa: C901
def translate(text: str):
    code: list[Code] = [Code(0, Opcode.NOP), Code(1, Opcode.NOP)]
    data: list[int] = []
    labels: dict[str, int] = {}
    words: dict[str, int] = {}
    prog_position: int = 2
    data_position: int = 4
    last_label: str = ""

    for line in text.splitlines():
        token = line.split(";", 1)[0].strip()
        if token == "":
            continue

        if token.endswith(":"):
            label = token.strip(":")
            assert label not in labels, "Redefinition of label: {}".format(label)
            labels[label] = prog_position
            last_label = label
        elif token.startswith("WORD"):
            word = token[4:].strip()
            word_data = parse_number(word)
            if last_label != "":
                prog_position = labels[last_label]
                if last_label not in words:
                    labels[last_label] = data_position
                    words[last_label] = data_position
            data.append(word_data)
            data_position += 1

        elif token.startswith("VEC"):
            sub_tokens = token.split(" ")
            assert len(sub_tokens) == 3, "Invalid vector format"
            mnemonic, vec, arg = sub_tokens
            vec_data = int(vec)
            assert vec_data in {0, 1}, "Invalid vector"
            code[vec_data].arg = arg

        elif " " in token:
            sub_tokens = token.split(" ")
            assert len(sub_tokens) == 2, "Invalid instruction: {}".format(token)
            mnemonic, arg = sub_tokens
            opcode = Opcode(mnemonic)
            code.append(Code(prog_position, opcode, arg))
            prog_position += 1
        else:
            opcode = Opcode(token)
            code.append(Code(prog_position, opcode, addressing=Addressing.NONE.value))
            prog_position += 1
    return MachineCode(second_stage(code, labels), data)

# flake8: noqa: C901
def second_stage(code: list[Code], labels: dict[str, int]):
    for instruction in code:
        if instruction.arg is not None:
            label = instruction.arg
            addressing = Addressing.DIRECT
            if label.startswith("["):
                if label.endswith("]"):
                    addressing = Addressing.INDIRECT
                elif label.endswith("]+"):
                    addressing = Addressing.POST_INC
                elif label.endswith("]-"):
                    addressing = Addressing.POST_DEC
            elif label.startswith("#"):
                addressing = Addressing.LOAD
            label = label.strip("#[]+-")
            instruction.addressing = addressing.value
            try:
                instruction.arg = str(parse_number(label))
                continue
            except ValueError:
                pass
            assert label in labels, "Label not defined: {}".format(label)
            instruction.arg = str(labels[label])
    return code


def parse_number(label: str) -> int:
    if label.startswith("0x"):
        return int(label[2:], 16)
    return int(label)


def write_code(filename: str, code: MachineCode):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, cls=MachineCodeEncoder, indent=4))


def main(source: str, target: str):
    with open(source, encoding="utf-8") as f:
        source_text = f.read()

    code = translate(source_text)

    write_code(target, code)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code.code))


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, src, tar = sys.argv
    main(src, tar)
