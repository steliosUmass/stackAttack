from memory import MemoryState
from stage_state import StageState
import instructions

class ExecuteStage():
    """
    Implements the execute stage in the pipelinne
    """

    def __init__( self ):
        self.current_instr = { 
                'Op': instructions.Op.NOOP,
                'operand_1': None,
                'operand_2': None,
                'operand_3': None
        }
        self.status = StageState.IDLE

    def execute_back_pass( self ):
        '''
        execute the backwards pass of the pipe
        '''
        
        should_squash = False
        # instruction is a branch 
        if self.current_instr.get( 'is_branch', False ):
            should_squash = instructions.branch_op( 
                    self.current_instr[ 'Op' ], 
                    self.current_instr[ 'Condition' ], 
                    self.current_instr[ 'Address' ],
                    self.current_instr[ 'Instr_offset' ]
            )

        # instruction is a memory access
        elif self.current_instr.get( 'is_mem_access', False ):
            mem_status = instructions.mem_op(  self.current_instr[ 'Op' ],self.current_instr[ 'Address' ] )
        # else, instruction is ALU operation
        else:
            instructions.alu_op(
                self.current_instr[ 'Op' ], 
                self.current_instr[ 'Operand_1' ], 
                self.current_instr[ 'Operand_2' ],
                self.current_instr[ 'Operand_3' ] 
            )

        self.state = StageState.IDLE if mem_status !=  MemoryState.BUSY else StageState.STALL
        # return status from Execute to decode
        return { 
                'should_squash': should_squash, 
                'status':  self.state
        }
    
    def execute_forward_pass( self, instr )
        '''
        execute forward pass of execute 
        '''
        
        # check if currently idle
        if self.state == StageState.IDLE:
            self.current_instr = instr
