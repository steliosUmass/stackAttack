from memory import MemoryState, Users
from stage_state import StageState
import registers
from decode import Decode


class Fetch:
    # TODO: Add support for instruction offset
    def __init__(self):
        # setting initial values for the fetch stage
        self.status = StageState.IDLE
        self.instr_per_word = 4
        self.load_data = None

    def load(self, address):
        # When the address is not in the cache it will return BUSY and stall the pipeline
        # else it will return the data and continue the pipeline

        # Set the fetch status to stall by default
        self.status = StageState.STALL
        return registers.MEMORY.read(address, Users.FETCH)

    def fetch(self, decode_state=StageState.STALL, should_issue=True):

        # check to see if fetch should do anything
        if should_issue:
            # Get the PC and the instruction offset
            pc = registers.PC
            offset = registers.INSTR_OFFSET
    
            self.load_data = self.load(pc)
            # Check if the memory or the decode stage is busy
            if self.load_data != MemoryState.BUSY and decode_state != StageState.STALL:
                # Set the fetch status to idle
                self.status = StageState.IDLE
    
                # Update the PC and the instruction offset
                registers.INSTR_OFFSET = offset + 1
                registers.PC = pc + registers.INSTR_OFFSET // self.instr_per_word
                registers.INSTR_OFFSET = registers.INSTR_OFFSET % self.instr_per_word
    
                # Extract the instruction from the load data
                load_data_pc = self.load_data[pc % 4]
                load_data_pc_offset = load_data_pc[offset]
                return load_data_pc_offset
    
        # If the memory or the decode stage is busy, return Op.NOOP
        return 45 + 2**7

    def fetch_back_pass(self, decode_status):
        if decode_status['status'] == StageState.STALL:
            self.status = StageState.STALL
        return decode_status

    def fetch_forward_pass(self, decode_status, should_issue):
        return self.fetch(decode_state=decode_status['status'], should_issue)
