from memory import MemoryState
from stage_state import StageState
import pipeline_options 
import instructions

class ExecuteStage():
    """
    Implements the execute stage in the pipelinne

    curr_instr
        current instuction that is executing

    status
        status of execution stage
    """

    def __init__( self ):
        self.curr_instr = { 
                'Op': instructions.Op.NOOP,
                'Operand_1': None,
                'Operand_2': None,
                'Operand_3': None
        }
        self.status = StageState.IDLE

    def execute_back_pass( self ):
        '''
        execute the backwards pass of the pipe
        this is where the operations get executed
        '''
        mem_status = None 
        squash = False
        # instruction is a branch 
        if self.curr_instr.get( 'is_branch', False ):
            squash = instructions.branch_op( 
                    self.curr_instr[ 'Op' ], 
                    self.curr_instr[ 'Condition' ], 
                    self.curr_instr[ 'Address' ],
                    self.curr_instr[ 'Instr_offset' ]
            )

        # instruction is a memory access
        elif self.curr_instr.get( 'is_mem_access', False ):
            mem_status = instructions.mem_op(  self.curr_instr[ 'Op' ], self.curr_instr[ 'Address' ] )
        # else, instruction is ALU operation
        else:
            instructions.alu_op(
                self.curr_instr[ 'Op' ], 
                self.curr_instr[ 'Operand_1' ], 
                self.curr_instr[ 'Operand_2' ],
                self.curr_instr[ 'Operand_3' ] 
            )

        self.state = StageState.IDLE if mem_status !=  MemoryState.BUSY else StageState.STALL

        # if idle, set instruction in progress status
        # this is used if the pipeline is off
        if self.state == StageState.IDLE:
            pipeline_options.INSTR_IN_PROGRESS = False
        
        # return status from Execute to decode
        return { 
                'squash': squash, 
                'status':  self.state
        }
    
    def execute_forward_pass( self, instr ):
        '''
        execute forward pass of execute 
        this is where the next instuction is set if not busy
        '''
        
        # check if currently idle
        if self.state == StageState.IDLE:
            self.curr_instr = instr

if __name__ == '__main__':
    import registers
    import pipeline_options
    registers.MEMORY.set_cache( False )
    e = ExecuteStage()
    print( e.execute_back_pass() )

    # try add
    instr = { 'Op': instructions.Op.ADD, 'Operand_1': 23,'Operand_2': 95, 'Operand_3': None }
    e.execute_forward_pass( instr )
    print( e.execute_back_pass() )
    print( registers.STACK )

    # try branch
    instr = { 'Op': instructions.Op.JMP_IF_1, 'Address': 100, 'Instr_offset': 1, 'Condition': 1, 'is_branch': True }
    e.execute_forward_pass( instr )
    print( e.execute_back_pass() )
    print( registers.PC )
    print( registers.INSTR_OFFSET )

    # try memory write access
    instr = { 'Op': instructions.Op.POP, 'Operand_1': None,'Operand_2': None, 'Operand_3': None }
    e.execute_forward_pass( instr )
    e.execute_back_pass( )

    instr = { 'Op': instructions.Op.STR_32, 'Address': 100, 'is_mem_access': True }
    state = StageState.STALL
    print( registers.POP )
    while state == StageState.STALL:
        e.execute_forward_pass( instr )
        response = e.execute_back_pass()
        state = response['status']
        print( response )
    print( registers.MEMORY.next_layer.mem[ 25 ] )
    
    # try memory read
    instr = { 'Op': instructions.Op.LDR_32, 'Address': 100, 'is_mem_access': True }
    state = StageState.STALL
    while state == StageState.STALL:
        e.execute_forward_pass( instr )
        response = e.execute_back_pass()
        state = response['status']
        print( response )
    print( registers.MEMORY.mem[ 9 ] )
    print( registers.PUSH )


     # try cache read
    instr = { 'Op': instructions.Op.LDR_32, 'Address': 100, 'is_mem_access': True }
    state = StageState.STALL
    while state == StageState.STALL:
        e.execute_forward_pass( instr )
        response = e.execute_back_pass()
        state = response['status']
        print( response )
    print( registers.MEMORY.mem[ 9 ] )
    print( registers.PUSH )
