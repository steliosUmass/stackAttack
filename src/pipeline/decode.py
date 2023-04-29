from instructions import Op
from memory import MemoryState
from stage_state import StageState
import registers
import decode_handler

from decode_types import alu, branch, memory, group
from execute import *


class Decode:
    def __init__(self):
        self.status = None
        self.counter = 0

        self.alu_op = alu.alu
        self.branch_op = branch.branch
        self.mem_op = memory.memory
        self.group_op = group.group
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
            'is_group': False,
            'squash': False
        }
        self.curr_instr = self.new_instr.copy()
        self.todo_op = {'instr': 45 + 2**7, 'squash': False}
        self.status = StageState.IDLE

    def decode(self):
        self.curr_instr = self.new_instr.copy()
        self.curr_instr['squash'] = self.todo_op['squash']
        op = self.todo_op['instr']

        # Pulls out bit 7 to get the type
        self.curr_instr['type'] = op >> 7

        if self.curr_instr['type'] == 0:
            # Pulls out bits 5-6 to get the OPCODE
            self.curr_instr['Op'] = Op((op >> 5) & 0x3)
            # Pulls out bits 0-4 to get the operand
            self.curr_instr['Operand_1'] = op & 0x1F

            self.curr_instr['is_alu'] = True
        else:
            # Pulls out bits 0-6 to get the OPCODE
            self.curr_instr['Op'] = Op((op & 0x7F) + 3)
            if self.curr_instr['Op'].name in self.alu_op.keys():
                self.curr_instr['is_alu'] = True
            elif self.curr_instr['Op'].name in self.branch_op.keys():
                self.curr_instr['is_branch'] = True
            elif self.curr_instr['Op'].name in self.mem_op.keys():
                self.curr_instr['is_mem_access'] = True
            elif self.curr_instr['Op'].name in self.group_op.keys():
                self.curr_instr['is_group'] = True

        # get varibales from stack if not squashed
        if not self.todo_op['squash'] and self.curr_instr['Op'].name in decode_handler.function_map:
            func = self.curr_instr['Op'].name
            self.curr_instr = self.function_map[func](self.curr_instr)

        return self.curr_instr

    def decode_forward_pass(self, todo_op):
        decoded_instr = self.curr_instr.copy()
        if self.status == StageState.STALL:
            return self.new_instr.copy()
        self.todo_op = todo_op
        return decoded_instr

    def decode_back_pass(self, execute_status):
        self.status = execute_status['status']
        self.todo_op['squash'] = self.todo_op['squash'] or execute_status['squash']
        # only decode if idle
        if self.status == StageState.IDLE:
            self.decode()
        return {'status': self.status, 'squash': execute_status['squash']}

    def get_state(self):
        state = ['State: {}'.format(self.status.name), 'Will Squash: {}'.format(
            'Yes' if self.curr_instr['squash'] else 'No')]

        if self.curr_instr['is_alu'] or self.curr_instr['is_group'] :
            state.append('instr: OP: {} {} {} {}'.format(self.curr_instr['Op'].name,
                                                         str(
                                                             self.curr_instr['Operand_1']) if self.curr_instr['Operand_1'] != None else '',
                                                         str(
                                                             self.curr_instr['Operand_2']) if self.curr_instr['Operand_2'] != None else '',
                                                         str(self.curr_instr['Operand_3']) if self.curr_instr['Operand_3'] != None else ''))
        elif self.curr_instr['is_mem_access']:
            state.append('instr: OP: {} Addr: {}'.format(self.curr_instr['Op'].name,
                                                         str(self.curr_instr['Address'])))
        elif self.curr_instr['is_branch']:
            state.append('instr: OP: {} Cond: {} Addr: {} Offset: {}'.format(self.curr_instr['Op'].name,
                                                                             str(self.curr_instr['Condition']), str(self.curr_instr['Address']), str(self.curr_instr['Instr_offset'])))
        else:
            state.append('instr: OP: {}'.format(self.curr_instr['Op'].name))
        return state
