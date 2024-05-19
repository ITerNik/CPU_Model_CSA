import json
from enum import Enum


class Word:
    def __init__(self, index: int, data: int):
        self.index: int = index
        self.data: int = data


class Addressing(Enum):
    DIRECT = 0
    INDIRECT = 1
    LOAD = 2
    POST_INC = 3
    POST_DEC = 4
    NONE = 5


class Opcode(str, Enum):
    NOP = 'NOP'
    HALT = 'HALT'
    EI = 'EI'
    DI = 'DI'
    RET = 'RET'
    ST = 'ST'
    JUMP = 'JUMP'
    LOAD = 'LOAD'
    JZ = 'JZ'
    JNZ = 'JNZ'
    JBE = 'JBE'
    JEV = 'JEV'
    CALL = 'CALL'
    IRET = 'IRET'


class Code:
    def __init__(self, index: int, opcode: Opcode, arg: str | None = None, addressing: Addressing = Addressing.DIRECT):
        self.index = index
        self.opcode = opcode
        self.arg = arg
        self.addressing = addressing


class CodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Code):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class WordEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Word):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

    class AddressingEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Addressing):
                return obj.__dict__
            return json.JSONEncoder.default(self, obj)

