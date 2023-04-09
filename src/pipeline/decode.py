from instructions import Op
from memory import MemoryState
from stage_state import StageState
import registers
import decode_handler

from decode_types import alu, branch, memory
from execute import *


class Decode:
    def __init__(self):
        self.status = None
        self.counter = 0

        self.alu_op = alu.alu
        self.branch_op = branch.branch
        self.mem_op = memory.memory
        self.function_map = decode_handler.function_map
        self.new_instr = {
            'type': 1,
            'Op': Op.NOOP,
            'Operand_1': None,
            'Operand_2': None,
            'Operand_3': None,
            'Address': None,
            'Condition': None,
            'is_alu': False,
            'is_branch': False,
            'is_mem_access': False,
            'squash': False
        }
        self.curr_instr = self.new_instr.copy()
        self.todo_opcode = 48

    def decode(self, op):
        self.curr_instr = self.new_instr.copy()
        # Pulls out bit 7 to get the type
        self.curr_instr['type'] = op >> 7

        if self.curr_instr['type'] == 0:
            # Pulls out bits 5-6 to get the OPCODE
            self.curr_instr['Op'] = Op((op >> 5) & 0x3)
            # Pulls out bits 0-4 to get the operand
            self.curr_instr['Operand_1'] = op & 0x1F
            # print(self.curr_instr['Op'], self.curr_instr['Operand_1'])
        else:
            # Pulls out bits 0-6 to get the OPCODE
            self.curr_instr['Op'] = Op(op & 0x7F)
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

    def decode_forward_pass(self, todo_op):
        decoded_instr = self.curr_instr.copy()
        if self.status == StageState.STALL:
            return self.new_instr.copy()
        self.todo_opcode = todo_op
        return decoded_instr

    def decode_back_pass(self, execute_status):
        if self.status == StageState.STALL:
            return self.new_instr.copy()
        self.decode(self.todo_opcode)
        self.status = execute_status
        return self.status
