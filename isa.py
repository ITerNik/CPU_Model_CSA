from __future__ import annotations

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
    CMP = "CMP"
    ADD = "ADD"
    NOP = "NOP"
    HALT = "HALT"
    EI = "EI"
    DI = "DI"
    RET = "RET"
    ST = "ST"
    JUMP = "JUMP"
    LOAD = "LOAD"
    JZ = "JZ"
    JNZ = "JNZ"
    JBE = "JBE"
    JEV = "JEV"
    CALL = "CALL"
    IRET = "IRET"


class Code:
    def __init__(self, index: int, opcode: Opcode, arg: str | None = None, addressing: int = 0):
        self.index = index
        self.opcode = opcode
        self.arg = arg
        self.addressing = addressing


class MachineCode:
    def __init__(self, code: list[Code], data: list[int]):
        self.code: list[Code] = code
        self.data: list[int] = data


class CodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Code):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class MachineCodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MachineCode):
            buf = []
            for code in obj.code:
                buf.append(code.__dict__)
            return {"code": buf, "data": obj.data}
        return json.JSONEncoder.default(self, obj)
