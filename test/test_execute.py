import unittest
import sys
import os

# Add execute object to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'src', 'pipeline' ) )

from execute import ExecuteStage
from stage_state import StageState
import registers
import instructions

class TestExecute( unittest.TestCase ):
    def setUp( self ):
        self.e = ExecuteStage()
    
    def test_init( self ):
        assert { 'squash': False, 'status': StageState.IDLE } == self.e.execute_back_pass(  )
        assert registers.STACK.top_index == -1
        assert registers.PC == 0
        assert registers.INSTR_OFFSET == 0
        assert registers.PUSH == 0
        assert registers.POP == 0
        assert registers.LINK == 0
    
    def test_stalled( self ):
        instr = { 'Op': instructions.Op.ADD, 'Operand_1': 23,'Operand_2': 95, 'Operand_3': None }
        self.e.execute_forward_pass( instr )
        self.e.status = StageState.STALL
        instr2 = { 'Op': instructions.Op.JMP_IF_1, 'Address': 100, 'Instr_offset': 1, 'Condition': 1, 'is_branch': True }
        self.e.execute_forward_pass( instr2 )
        assert self.e.curr_instr == instr

    def test_add( self ):
        instr = { 'Op': instructions.Op.ADD, 'Operand_1': 23,'Operand_2': 95, 'Operand_3': None }
        self.e.execute_forward_pass( instr )
        assert { 'squash': False, 'status': StageState.IDLE } == self.e.execute_back_pass(  )
        assert registers.STACK.stack[ 0 ] == 23 + 95
    
    def test_squash( self ):
        instr = { 'Op': instructions.Op.ADD, 'Operand_1': 23,'Operand_2': 95, 'Operand_3': None, 'squash': True }
        self.e.execute_forward_pass( instr )
        assert { 'squash': False, 'status': StageState.IDLE } == self.e.execute_back_pass(  )
        assert registers.STACK.top_index == -1

    def test_branch_taken( self ):
        instr = { 'Op': instructions.Op.JMP_IF_1, 'Address': 100, 'Instr_offset': 1, 'Condition': 1, 'is_branch': True }
        self.e.execute_forward_pass( instr )
        assert { 'squash': True, 'status': StageState.IDLE } == self.e.execute_back_pass(  )
        assert registers.PC == 100
        assert registers.INSTR_OFFSET == 1
    
    def test_branch_not_taken( self ):
        instr = { 'Op': instructions.Op.JMP_IF_1, 'Address': 300, 'Instr_offset': 1, 'Condition': 0, 'is_branch': True }
        self.e.execute_forward_pass( instr )
        assert { 'squash': False, 'status': StageState.IDLE } == self.e.execute_back_pass(  )
        assert registers.PC == 0
        assert registers.INSTR_OFFSET == 0

    def test_mem_read( self ):
         instr = { 'Op': instructions.Op.STR_32, 'Address': 100, 'is_mem_access': True }
         registers.POP = 89
         self.e.execute_forward_pass( instr )
         for i in range( 4 ):
            assert { 'squash': False, 'status': StageState.STALL } == self.e.execute_back_pass(  )
         assert { 'squash': False, 'status': StageState.IDLE } == self.e.execute_back_pass(  )
    
    def tearDown( self ):
        registers.STACK = registers.Stack( 32 )
        registers.PC = 0
        registers.INSTR_OFFSET = 0
        registers.PUSH = 0
        registers.POP = 0
        registers.LINK = 0
