from execute import ExecuteStage

class PipeLine( ):
    """
    Used step or run through simulation
    """

    def __init__():
        self.cycle = 0
        self.pipeline_on = True
        self.halt = False
        self.execute = ExecuteStage()
    
    def step():
        execute_status = execute_back_pass( self ):

        # increment cycle
        self.cycle += 1


    def run():
        '''run simulation until halt instr is hit'''
        while not self.halt:
            self.step( )

    def set_pipeline_status( is_on ):
        self.pipeline_on= is_on
