from __future__ import annotations

import json
import logging
import sys
from enum import Enum

from isa import Addressing, Code, MachineCode, Opcode

MEMORY_START = 4
DATA_MEMORY_SIZE = 2**16
INSTR_LIMIT = 500


class ALUOptions(Enum):
    LEFT_ZERO = 0
    RIGHT_ZERO = 1
    NOT_LEFT = 2
    NOT_RIGHT = 3
    INC = 4
    DEC = 5


class DataPath:
    def __init__(self, data_memory, data_memory_size, input_buffer):
        assert data_memory_size > len(data_memory) + MEMORY_START, "Data_memory size is not enough"
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * MEMORY_START + data_memory + [0] * (data_memory_size - len(data_memory) - MEMORY_START)
        self.ar = 0
        self.acc = 0
        self.dr = 0
        self.cr = Code(0, Opcode.NOP)
        self.input_buffer = input_buffer
        self.output_buffer = []

    def signal_latch_ar(self, options=None):
        if options is None:
            assert self.cr.arg is not None, "Internal error"
            self.ar = int(self.cr.arg)
        else:
            self.ar = self.process_alu(options)

        assert 0 <= self.ar < self.data_memory_size, "out of memory: {}".format(self.ar)

    def signal_latch_acc(self, options):
        self.acc = self.process_alu(options)

    def process_alu(self, options: list[ALUOptions] = []):
        left = self.dr
        right = self.acc

        if ALUOptions.LEFT_ZERO in options:
            left = 0
        if ALUOptions.RIGHT_ZERO in options:
            right = 0
        if ALUOptions.NOT_LEFT in options:
            left = ~left
        if ALUOptions.NOT_RIGHT in options:
            right = ~right
        if ALUOptions.INC in options:
            left += 1
        elif ALUOptions.DEC in options:
            left -= 1

        return left + right

    def signal_data_out(self):
        if self.ar == 1:
            if 0 <= self.dr <= 256:
                self.output_buffer.append(chr(self.dr))
            else:
                self.output_buffer.append(str(self.dr))
            logging.debug("output: %s", repr(self.dr))
        self.data_memory[self.ar] = self.dr

    def signal_data_in(self):
        if self.ar == 0:
            if len(self.input_buffer) <= 0:
                raise EOFError()
            self.dr = ord(self.input_buffer.pop()[1])
            logging.debug("input: %s", repr(self.data_memory[0]))
        else:
            self.signal_latch_dr()

    def signal_latch_dr(self, options=None):
        if options is None:
            self.dr = self.data_memory[self.ar]
        else:
            self.dr = self.process_alu(options)

    def zero(self):
        return self.acc == 0

    def even(self):
        return (self.acc & 1) == 0

    def negative(self):
        return self.acc < 0


class ControlUnit:
    def __init__(self, program_memory: list[Code], data_path: DataPath):
        self.ei = True
        self.program_memory: list[Code] = program_memory
        self.pc = 2
        self.sp = 0
        self.call_stack: list[int] = len(program_memory) * [0]
        self.data_path: DataPath = data_path
        self._tick = 0
        self.int_req = False
        self.int_vec = 0
        self.be = False

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    def address_fetch(self, instr: Code):
        addr = Addressing(instr.addressing)
        if addr is Addressing.NONE:
            return
        assert instr.arg is not None, "Internal error {} {}".format(instr.opcode, instr.index)
        if addr is Addressing.DIRECT:
            self.data_path.signal_latch_ar()
            self.tick()

            self.data_path.signal_data_in()
            self.tick()
        elif addr is Addressing.LOAD:
            self.data_path.dr = int(instr.arg)
            self.tick()
        elif addr is Addressing.INDIRECT:
            self.data_path.signal_latch_ar()
            self.tick()

            self.data_path.signal_data_in()
            self.tick()

            self.data_path.signal_latch_ar([ALUOptions.RIGHT_ZERO])
            self.tick()

            self.data_path.signal_data_in()
            self.tick()

        elif addr in {Addressing.POST_INC, Addressing.POST_DEC}:
            self.data_path.signal_latch_ar()
            self.tick()

            self.data_path.signal_data_in()
            self.tick()

            self.data_path.signal_latch_dr(
                [ALUOptions.RIGHT_ZERO, ALUOptions.INC if addr is Addressing.POST_INC else ALUOptions.DEC]
            )
            self.tick()

            self.data_path.signal_data_out()
            self.data_path.signal_latch_ar(
                [ALUOptions.RIGHT_ZERO, ALUOptions.DEC if addr is Addressing.POST_INC else ALUOptions.INC]
            )
            self.tick()

            self.data_path.signal_data_in()
            self.tick()

    def signal_latch_pc(self, sel: Opcode):
        if sel in {Opcode.JZ, Opcode.JBE, Opcode.JUMP, Opcode.JEV, Opcode.JNZ}:
            instr: Code = self.program_memory[self.pc]
            assert instr.arg is not None, "Internal error"
            self.pc = int(instr.arg) - 1
        elif sel is Opcode.IRET:
            self.signal_latch_sp("-1")
            self.pc = self.call_stack[self.sp]
        else:
            self.pc += 1

    def signal_latch_sp(self, sel):
        if sel == "-1":
            self.sp -= 1
        elif sel == "+1":
            self.sp += 1

    def signal_cur_instr(self):
        self.data_path.cr = self.program_memory[self.pc]

    def decode_and_execute_control_flow_instruction(self, instr: Code):
        assert instr.addressing not in {
            Addressing.POST_INC,
            Addressing.POST_DEC,
            Addressing.INDIRECT,
        }, "Control flow instruction addressing conflict"
        opcode: Opcode = Opcode(instr.opcode)

        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode is Opcode.JUMP:
            self.signal_latch_pc(opcode)
            self.tick()

            return True

        if opcode is Opcode.JZ:
            if self.data_path.zero():
                self.signal_latch_pc(opcode)

            self.tick()
            return True

        if opcode is Opcode.JNZ:
            if not self.data_path.zero():
                self.signal_latch_pc(opcode)

            self.tick()

            return True

        if opcode is Opcode.JBE:
            if self.be:
                self.signal_latch_pc(opcode)

            self.tick()

            return True

        if opcode is Opcode.JEV:
            if self.data_path.even():
                self.signal_latch_pc(opcode)

            self.tick()

            return True

        return False

    # flake8: noqa: C901
    def decode_and_execute_instruction(self):
        self.signal_cur_instr()
        instr = self.data_path.cr
        opcode = Opcode(instr.opcode)

        if self.decode_and_execute_control_flow_instruction(instr):
            self.handle_int()
            return

        self.address_fetch(instr)

        if opcode is Opcode.LOAD:
            self.data_path.signal_latch_acc([ALUOptions.RIGHT_ZERO])
            self.tick()

        elif opcode is Opcode.ST:
            self.data_path.signal_latch_dr([ALUOptions.LEFT_ZERO])
            self.data_path.signal_data_out()
            self.tick()
        elif opcode is Opcode.NOP:
            pass
        elif opcode is Opcode.DI:
            self.ei = False
            self.tick()
        elif opcode is Opcode.EI:
            self.ei = True
            self.tick()
        elif opcode in {Opcode.IRET, Opcode.RET}:
            assert len(self.call_stack) > 0, "Internal error"
            self.signal_latch_sp("-1")
            self.tick()

            self.pc = self.call_stack[self.sp]
            if opcode is Opcode.IRET:
                self.ei = True
            self.tick()
        elif opcode is Opcode.CALL:
            self.call_stack[self.sp] = self.pc
            self.tick()

            self.signal_latch_sp("+1")
            self.pc = int(instr.arg) - 1
            self.tick()
        elif opcode is Opcode.ADD:
            self.data_path.signal_latch_acc([])
            self.tick()
        elif opcode is Opcode.CMP:
            tmp = self.data_path.acc
            self.data_path.signal_latch_acc([ALUOptions.NOT_LEFT, ALUOptions.INC])
            self.be = not self.data_path.negative()
            self.data_path.acc = tmp
            self.tick()
        else:
            raise ValueError(f"{opcode}")

        self.handle_int()

    def __repr__(self):
        state_repr = "TICK: {:3} PC: {:3} AR: {:3} DR {:3} SP {:3} MEM_OUT: {} ACC: {}".format(
            self._tick,
            self.pc,
            self.data_path.ar,
            self.data_path.dr,
            self.sp,
            self.data_path.data_memory[self.data_path.ar],
            self.data_path.acc,
        )

        instr = self.program_memory[self.pc]
        opcode = instr.opcode
        instr_repr = str(opcode)

        if instr.arg is not None:
            instr_repr += " {}".format(instr.arg)

        return "{} {}".format(state_repr, instr_repr)

    def handle_int(self):
        if (
            self.ei
            and len(self.data_path.input_buffer) > 0
            and self.data_path.input_buffer[-1][0] <= self.current_tick()
        ):
            self.ei = False
            self.call_stack[self.sp] = self.pc
            self.tick()

            self.signal_latch_sp("+1")
            self.pc = int(self.program_memory[self.int_vec].arg) - 1
        self.signal_latch_pc(Opcode.NOP)
        self.tick()


def simulation(code, input_tokens, data_memory, data_memory_size, limit):
    data_path = DataPath(data_memory, data_memory_size, input_tokens)
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", control_unit)
    except (StopIteration, EOFError):
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")
    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(code_file, input_file):
    with open(code_file, encoding="utf-8") as file:
        code = json.loads(file.read())
        machine_code = MachineCode(list(map(lambda d: Code(**d), code["code"])), code["data"])
    with open(input_file, encoding="utf-8") as file:
        input_text = sorted(json.loads(file.read()), reverse=True)

    output, instr_counter, ticks = simulation(
        machine_code.code, input_text, machine_code.data, DATA_MEMORY_SIZE, INSTR_LIMIT
    )

    print("".join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
