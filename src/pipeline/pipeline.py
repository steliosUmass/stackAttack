from execute import ExecuteStage
from decode import Decode
from fetch import Fetch
import instructions

class PipeLine():
    """
    Used step or run through simulation
    """

    def __init__(self):
        self.cycle = 0
        self.pipeline_on = True
        self.halt = False
        self.execute = ExecuteStage()
        self.decode = Decode()
        self.fetch = Fetch()

    def step(self):
        execute_status = self.execute.execute_back_pass()
        decode_status = self.decode.decode_back_pass(execute_status)
        # check if current insturction are NOOP
        # this is needed in non pipline mode to see if fetch
        # should issue an instruction
        should_issue = ( self.pipeline_on or 
             ( self.execute.curr_instr[ 'Op' ] == instructions.Op.NOOP 
                    and  self.decode.curr_instr[ 'Op' ] == instructions.Op.NOOP ) )

        # check to see if halt was executed
        self.halt = execute_status.get( 'finish', False )

        self.fetch.fetch_back_pass( decode_status )
        curr_opcode = self.fetch.fetch_forward_pass(decode_status, should_issue )
        curr_instr = self.decode.decode_forward_pass(curr_opcode)
        print( curr_opcode )
        print( curr_instr )
        print( self.execute.curr_instr )
        print()
        print()
        self.execute.execute_forward_pass(curr_instr)
        
        # increment cycle
        self.cycle += 1
    def run(self):
        '''run simulation until halt instr is hit'''
        while not self.halt:
            self.step()

    def set_pipeline_status(self, is_on):
        self.pipeline_on = is_on
