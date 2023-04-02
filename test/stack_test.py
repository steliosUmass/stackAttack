import unittest
import sys
import os

# Add stack object to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'src', 'pipeline' ) )
import registers

class TestStack( unittest.TestCase ):
    def setUp( self ):
        self.stack = registers.Stack( 32 )
    def test_push( self ):
        self.stack.push( 156 )
        assert self.stack.stack == [ 156 ] + [ 0 ] * 31

    def test_mulit_push( self ):
        test_stack = []
        for i in range( 32 ):
            self.stack.push( 34 )
            test_stack.append( 34 )
            assert self.stack.stack == test_stack + [ 0 ] * ( 31 - i )
            assert self.stack.top_index == i
    
    def test_overflow( self ):
       for i in range( 32 ):
            self.stack.push( 34 )
       for i in range( 32 ):
            self.stack.push( 198 )
            test_stack = [ 34 ] * ( 31 - i ) + [ 198 ] * ( i + 1 ) 
            assert self.stack.stack == test_stack 

    def test_pop( self ):
        for i in range( 32 ):
            self.stack.push( i )
        for i in range( 31, -1, -1 ):
            assert self.stack.top_index == i
            self.stack.pop()
            assert registers.POP == i
    def test_pop_empty( self ):
        assert self.stack.top_index == -1
        self.stack.pop()
        assert self.stack.top_index == -1
