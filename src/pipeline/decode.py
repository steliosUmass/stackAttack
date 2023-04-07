from instructions import Op
from memory import MemoryState
from stage_state import StageState
import registers
import pipeline_options
import decode_handler

from decode_types import alu, branch, memory


class Decode:
    def __init__(self):
        self.status = StageState.IDLE
        self.counter = 0

        self.alu_op = alu.alu
        self.branch_op = branch.branch
        self.mem_op = memory.memory
        self.function_map = decode_handler.function_map
        self.new_instr = {
            'Op': Op.NOOP,
            'Operand_1': None,
            'Operand_2': None,
            'Operand_3': None,
            'is_alu': False,
            'is_branch': False,
            'is_mem_access': False
        }
        self.curr_instr = self.new_instr.copy()

    def decode(self, op):
        self.curr_instr = self.new_instr.copy()
        self.curr_instr['Op'] = Op(op)

        if self.curr_instr['Op'].name in self.alu_op.keys():
            self.curr_instr['is_alu'] = True
        elif self.curr_instr['Op'].name in self.branch_op.keys():
            self.curr_instr['is_branch'] = True
        elif self.curr_instr['Op'].name in self.mem_op.keys():
            self.curr_instr['is_mem_access'] = True

        if self.curr_instr['Op'].name in decode_handler.function_map:
            func = self.curr_instr['Op'].name
            self.curr_instr = self.function_map[func](self.curr_instr)
        return self.curr_instr

    def decode_forward_pass(self, curr_instr):
        self.status = StageState.IDLE
        return curr_instr

    def decode_back_pass(self):
        return {
            'status': self.status
        }