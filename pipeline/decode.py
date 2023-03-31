from instructions import Op
from stage_state import StageState

class Decode:
    def __init__(self):
        self.status = StageState.IDLE
        self.counter = 0

    def decode(self, op):
        return Op(op)
