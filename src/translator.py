import json
import sys

from isa import Term, Code, Opcode, CodeEncoder


def translate(text: str):
    code = []
    data =[]
    labels: dict[str, int] = {}
    prog_position: int = 0
    data_position: int = 4
    last_label: str = ''

    for line in text.splitlines():
        token = line.split(';', 1)[0].strip()
        if token == '':
            continue

        if token.endswith(":"):
            label = token.strip(":")
            assert label not in labels, "Redefinition of label: {}".format(label)
            labels[label] = prog_position
            last_label = label
            prog_position += 1
        elif token.startswith("WORD"):
            word = token[4:].strip()
            prog_position = labels[last_label]
            if last_label not in labels:
                labels[last_label] = data_position
            data.append(Code(data_position, Opcode.NOP, word))
            data_position += 1
        elif " " in token:
            sub_tokens = token.split(" ")
            assert len(sub_tokens) == 2, "Invalid instruction: {}".format(token)
            mnemonic, arg = sub_tokens
            opcode = Opcode(mnemonic)
            code.append(Code(prog_position, opcode, arg))
            prog_position += 1
        else:
            opcode = Opcode(token)
            code.append(Code(prog_position, opcode))
            prog_position += 1
    return code, labels, data


def main(source: str, target: str):
    with open(source, encoding="utf-8") as f:
        source_text = f.read()

    code, labels, data = translate(source_text)
    print(json.dumps(code, cls=CodeEncoder, separators=(",\n", " : ")))
    print(labels)
    print(json.dumps(data, cls=CodeEncoder, separators=(",\n", " : ")))


if __name__ == '__main__':
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, src, tar = sys.argv
    main(src, tar)
