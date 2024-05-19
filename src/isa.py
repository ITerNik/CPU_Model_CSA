import json
from enum import Enum


class Term:
    def __init__(self, line: int, pos: int, symbol: str):
        self.line = line
        self.pos = pos
        self.symbol = symbol


class Addressing(Enum):
    DIRECT = 0
    INDIRECT = 1
    LOAD = 2
    POST_INC = 3
    POST_DEC = 4


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
    def __init__(self, index: int, opcode: Opcode, arg: str = None, term: Term = None):
        self.index = index
        self.opcode = opcode
        self.arg = arg
        self.term = term


class CodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Code):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

