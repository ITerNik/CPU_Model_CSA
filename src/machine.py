import json
import logging
import sys
from enum import Enum

from isa import MachineCode, Code, Opcode, Addressing


ADDRESS_LENGTH = 2**24
WORD_LENGTH = 2**32


class ALUOptions(Enum):
    LEFT_ZERO = 0,
    RIGHT_ZERO = 1,
    NEG_LEFT = 2,
    NEG_RIGHT = 3,
    INC = 4


class DataPath:
    def __init__(self, data_memory, data_memory_size, input_buffer):
        assert data_memory_size > len(data_memory) + 4, "Data_memory size is not enough"
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * 4 + data_memory + [0] * (data_memory_size - len(data_memory) - 4)
        self.ar = 0
        self.acc = 0
        self.dr = 0
        self.cr = Code(0, Opcode.NOP)
        self.input_buffer = input_buffer
        self.output_buffer = []

    def signal_latch_ar(self, sel: int, options=[]):
        sel_addr = Addressing(sel)
        if sel_addr is not Addressing.NONE:
            assert self.cr.arg is not None, 'Internal error'
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
        if ALUOptions.NEG_LEFT in options:
            left = -left
        if ALUOptions.NEG_RIGHT in options:
            right = -right
        if ALUOptions.INC in options:
            left += 1

        return left + right

    def signal_data_out(self):
        if self.ar == 1:
            self.output_buffer.append(chr(self.dr))
        self.data_memory[self.ar] = self.dr
        # logging.debug("input: %s", repr(symbol))

    def signal_data_in(self):
        self.signal_latch_dr()
        # logging.debug("input: %s", repr(symbol))

    def signal_latch_dr(self, options=[], select_data=True):
        if select_data:
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
        self.program_memory: list[Code] = program_memory
        self.pc = 0
        self.sp = 0
        self.call_stack: list[int] = []
        self.data_path: DataPath = data_path
        self._tick = 0
        self.int_req = False
        self.int_vec = 0
        self.be = False

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    def signal_latch_pc(self, sel: Opcode):
        if sel in {Opcode.JZ, Opcode.JBE, Opcode.JUMP, Opcode.JEV, Opcode.JNZ}:
            instr: Code = self.program_memory[self.pc]
            assert instr.arg is not None, 'Internal error'
            self.pc = int(instr.arg) - 1
        elif sel is Opcode.IRET:
            self.pc = self.call_stack.pop()
        else:
            self.pc += 1

    def signal_latch_sp(self, sel):
        if sel == '-1':
            self.sp -= 1
        elif sel == '1':
            self.sp += 1

    def signal_cur_instr(self):
        self.data_path.cr = self.program_memory[self.pc]

    def decode_and_execute_control_flow_instruction(self, instr: Code):
        opcode: Opcode = Opcode(instr.opcode)
        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode is Opcode.JUMP:
            addr = instr.arg
            assert addr is not None, 'Internal error'
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

            self.signal_latch_pc(Opcode.NOP)

            return True

        return False

    def decode_and_execute_instruction(self):
        """Основной цикл процессора. Декодирует и выполняет инструкцию.

        Обработка инструкции:

        1. Проверить `Opcode`.

        2. Вызвать методы, имитирующие необходимые управляющие сигналы.

        3. Продвинуть модельное время вперёд на один такт (`tick`).

        4. (если необходимо) повторить шаги 2-3.

        5. Перейти к следующей инструкции.

        Обработка функций управления потоком исполнения вынесена в
        `decode_and_execute_control_flow_instruction`.
        """

        self.signal_cur_instr()
        instr = self.data_path.cr
        opcode = Opcode(instr.opcode)

        if self.decode_and_execute_control_flow_instruction(instr):
            return

        if opcode is Opcode.LOAD:
            self.data_path.signal_latch_ar(instr.addressing)
            self.tick()

            self.data_path.signal_data_in()
            self.data_path.signal_latch_acc([ALUOptions.RIGHT_ZERO])
            self.tick()

        elif opcode is Opcode.ST:
            self.data_path.signal_latch_ar(instr.addressing)
            self.tick()

            self.data_path.signal_latch_dr([ALUOptions.LEFT_ZERO], select_data=False)
            self.data_path.signal_data_out()
            self.tick()
        else:
            raise ValueError(f"Invalid opcode {opcode}")

        self.signal_latch_pc(opcode)

    def __repr__(self):
        """Вернуть строковое представление состояния процессора."""
        state_repr = "TICK: {:3} PC: {:3} ADDR: {:3} MEM_OUT: {} ACC: {}".format(
            self._tick,
            self.program_counter,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.acc,
        )

        instr = self.program_memory[self.pc]
        opcode = instr.opcode
        instr_repr = str(opcode)

        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])

        if "term" in instr:
            term = instr["term"]
            instr_repr += "  ('{}'@{}:{})".format(term.symbol, term.line, term.pos)

        return "{} \t{}".format(state_repr, instr_repr)


def simulation(code, input_tokens, data_memory, data_memory_size, limit):
    data_path = DataPath(data_memory, data_memory_size, input_tokens)
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    # logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            # logging.debug("%s", control_unit)
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")
    # logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(code_file, input_file):
    with open(code_file, encoding="utf-8") as file:
        code = json.loads(file.read())
        machine_code = MachineCode(list(map(lambda d: Code(**d), code['code'])), code['data'])
    with open(input_file,  encoding="utf-8") as file:
        input_text = sorted(json.loads(file.read()))

    print(simulation(machine_code.code, input_text, machine_code.data, 256, 100))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
