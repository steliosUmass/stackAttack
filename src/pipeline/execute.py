from memory import MemoryState
from stage_state import StageState
import instructions
import registers


class ExecuteStage():
    """
    Implements the execute stage in the pipelinne

    curr_instr
        current instuction that is executing

    status
        status of execution stage
    """

    def __init__(self):
        self.curr_instr = {
            'Op': instructions.Op.NOOP,
            'Operand_1': None,
            'Operand_2': None,
            'Operand_3': None,
            'is_alu': False,
            'is_mem_access': False,
            'is_branch': False,
            'is_crypto': False

        }
        self.status = StageState.IDLE
        self.squash = False
        self.alu_executer = instructions.AluExecuter()
        self.memory_executer = instructions.MemoryExecuter()
        self.cypto_executer = instructions.CryptoExecuter()
        self.last_executed = self.curr_instr
        self.no_op_instr = 0
        self.alu_instr = 0
        self.branch_instr = 0
        self.crypto_instr = 0
        self.mem_instr = 0

    def execute_back_pass(self):
        '''
        execute the backwards pass of the pipe
        this is where the operations get executed
        '''
        self.squash = False
        self.last_executed = self.curr_instr

        # check to see if current instruction should be squashed

        if not self.curr_instr.get('squash', False):

            # if instruction is halt, return with finish flag
            if self.curr_instr['Op'] == instructions.Op.HALT:
                return {
                    'squash': self.squash,
                    'status':  self.status,
                    'finish': True
                }

            # instruction is a branch
            if self.curr_instr.get('is_branch', False):
                self.branch_instr += 1
                self.squash = self.alu_executer.branch_op(
                    self.curr_instr['Op'],
                    self.curr_instr['Condition'],
                    self.curr_instr['Address'],
                    self.curr_instr['Instr_offset']
                )

            # instruction is a memory access
            elif self.curr_instr.get('is_mem_access', False):
                self.mem_instr += 1
                self.status = self.memory_executer.mem_op(
                    self.curr_instr['Op'], self.curr_instr['Address'])
            elif self.curr_instr.get( 'is_crypto', False ):
                self.crypto_instr += 1 
                self.status = self.cypto_executer.crypto_op(
                    self.curr_instr['Op'],
                    self.curr_instr['Operand_1'],
                    self.curr_instr['Operand_2'],
                    self.curr_instr['Operand_3']
                )

            # else, instruction is ALU operation
            else:
                if self.curr_instr['Op'] == instructions.Op.NOOP:
                    self.no_op_instr += 1
                else:
                    self.alu_instr += 1
                self.alu_executer.alu_op(
                    self.curr_instr['Op'],
                    self.curr_instr['Operand_1'],
                    self.curr_instr['Operand_2'],
                    self.curr_instr['Operand_3']
                )

        # return status from Execute to decode
        return {
            'squash': self.squash,
            'status':  self.status
        }

    def execute_forward_pass(self, instr):
        '''
        execute forward pass of execute 
        this is where the next instuction is set if not busy
        '''

        # check if currently idle
        if self.status == StageState.IDLE:
            self.curr_instr = instr

    def get_state(self):
        state = ['Status: {}'.format(self.status.name),
            'Will Squash: {}'.format( 'Yes' if self.last_executed.get( 'squash', False ) else 'No' ),
            'Will Send Squash: {}'.format( 'Yes' if self.squash else 'No')
        ]

        if self.last_executed['is_alu'] or self.last_executed['is_crypto'] :
            state.append('instr: OP: {} {} {} {}'.format(self.last_executed['Op'].name,
                                                         str(
                                                             self.last_executed['Operand_1']) if self.last_executed['Operand_1'] != None else '',
                                                         str(
                                                             self.last_executed['Operand_2']) if self.last_executed['Operand_2'] != None else '',
                                                         str(self.last_executed['Operand_3']) if self.last_executed['Operand_3'] != None else ''))
        elif self.last_executed['is_mem_access']:
            state.append('instr: OP: {} Addr: {}'.format(self.last_executed['Op'].name,
                                                         str(self.last_executed['Address'])))
        elif self.last_executed['is_branch']:
            state.append('instr: OP: {} Cond: {} Addr: {} Offset: {}'.format(self.last_executed['Op'].name,
                                                                             str(self.last_executed['Condition']), str(self.last_executed['Address']), str(self.last_executed['Instr_offset'])))
        else:
            state.append('instr: OP: {}'.format(self.last_executed['Op'].name))
        return state


if __name__ == '__main__':
    import registers
    registers.MEMORY.set_cache(False)
    e = ExecuteStage()
    print(e.execute_back_pass())

    # try add
    instr = {'Op': instructions.Op.ADD, 'Operand_1': 23,
             'Operand_2': 95, 'Operand_3': None}
    e.execute_forward_pass(instr)
    print(e.execute_back_pass())
    print(registers.STACK)

    # try branch
    instr = {'Op': instructions.Op.JMP_IF_1, 'Address': 100,
             'Instr_offset': 1, 'Condition': 1, 'is_branch': True}
    e.execute_forward_pass(instr)
    print(e.execute_back_pass())
    print(registers.PC)
    print(registers.INSTR_OFFSET)

    # try memory write access
    instr = {'Op': instructions.Op.POP, 'Operand_1': None,
             'Operand_2': None, 'Operand_3': None}
    e.execute_forward_pass(instr)
    e.execute_back_pass()

    instr = {'Op': instructions.Op.STR_32,
             'Address': 100, 'is_mem_access': True}
    state = StageState.STALL
    print(registers.POP)
    while state == StageState.STALL:
        e.execute_forward_pass(instr)
        response = e.execute_back_pass()
        state = response['status']
        print(response)
    print(registers.MEMORY.next_layer.mem[25])

    # try memory read
    instr = {'Op': instructions.Op.LDR_32,
             'Address': 100, 'is_mem_access': True}
    state = StageState.STALL
    while state == StageState.STALL:
        e.execute_forward_pass(instr)
        response = e.execute_back_pass()
        state = response['status']
        print(response)
    print(registers.MEMORY.mem[9])
    print(registers.PUSH)

    # try cache read
    instr = {'Op': instructions.Op.LDR_32,
             'Address': 100, 'is_mem_access': True}
    state = StageState.STALL
    while state == StageState.STALL:
        e.execute_forward_pass(instr)
        response = e.execute_back_pass()
        state = response['status']
        print(response)
    print(registers.MEMORY.mem[9])
    print(registers.PUSH)
