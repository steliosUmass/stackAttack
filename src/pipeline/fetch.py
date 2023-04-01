from memory import MemoryState, Users
from stage_state import StageState
import registers
from decode import Decode


class Fetch:
    def __init__(self):
        self.status = StageState.IDLE
        self.counter = 0
        self.instr_per_word = 4

    def load(self, address):
        self.status = StageState.STALL
        return registers.MEMORY.read(address, Users.FETCH)

    def fetch(self, pc=registers.PC, offset=registers.INSTR_OFFSET, decode_state=StageState.STALL):
        load_data = self.load(pc)
        if load_data != MemoryState.BUSY and decode_state != StageState.STALL:
            self.status = StageState.IDLE
            registers.INSTR_OFFSET = offset + 1
            registers.PC = pc + registers.INSTR_OFFSET // self.instr_per_word
            registers.INSTR_OFFSET = registers.INSTR_OFFSET % self.instr_per_word
            load_data_pc = load_data[pc % 4]
            load_data_pc_offset = load_data_pc[offset]
            return load_data_pc_offset

        return 48
