# got example from https://pythonbasics.org/qt-designer-python/

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from tkinter import filedialog
import tkinter 
import view_models
import sim_gui
import sys
import os

# Add pipeline directory to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'pipeline' ) )
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ )  ) ) ), 'tools' ) )

from pipeline import PipeLine
import registers
from disassembler import dissassemble

class Simulator(QtWidgets.QMainWindow, sim_gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Simulator, self).__init__(parent)
        self.setupUi(self)

        # init combo box to choose between ram and cache
        self.memCombo.addItems( [ 'RAM', 'CACHE'] )

        # set check state for cache on and pipeline on
        # also assign signals
        self.cacheOn.setChecked( True )
        self.pipeOn.setChecked( True )
        self.cacheOn.stateChanged.connect( self.set_cache_enable )
        self.pipeOn.stateChanged.connect( self.set_pipeline_enable )

        # set signal for combo box between memory and cache ( and call it with index 0 )
        self.memCombo.currentIndexChanged.connect( self.index_changed_memCombo )
        self.index_changed_memCombo( 0 )

        # init register table
        self.regView.setModel( view_models.RegisterModel( 
            registers.PC, registers.INSTR_OFFSET, registers.LINK, registers.PUSH, registers.POP, 0 ) )

        # add signal to load program
        self.LoadButton.clicked.connect( self.load_program )           

        # create pipeline object to controll simulation
        self.pipeline = PipeLine( )

        # add signal for running sim
        self.runButton.clicked.connect( self.run )

        # add signal for step sim
        self.stepButton.clicked.connect( self.step )

        
    def update_gui( self ):
        '''updates the gui with the current state of the simulator'''
        # update memory
        self.index_changed_memCombo( self.memCombo.currentIndex() )
        
        # update registers 
        self.regView.setModel( view_models.RegisterModel( 
            registers.PC, registers.INSTR_OFFSET, registers.LINK, registers.PUSH, registers.POP, self.pipeline.cycle ) )

        stack_list = registers.STACK.stack[ : registers.STACK.top_index ] 
        if registers.STACK.top_index  < 0:
            stack_list = []
        self.stackView.setModel( view_models.StackModel( stack_list ) )

    def step( self ):
        '''step through one cycle'''
        self.pipeline.step( )
        self.update_gui( ) 
    
    def run( self ):
        '''runs simulation untill halt instr is reached'''
        self.pipeline.step( )
        self.update_gui( ) 

    def index_changed_memCombo( self, index ):
        '''updates the mem table to show either cache or ram based on comboBox index'''
        if index == 0:
            # show ram
            self.memTable.setModel( view_models.RamModel( registers.MEMORY.next_layer.mem ) )
        elif index == 1:
            # show cache
            self.memTable.setModel( view_models.CacheModel( registers.MEMORY.tag, registers.MEMORY.mem, registers.MEMORY.valid ) )

    def set_cache_enable( self, state ):
        '''activates or disables cache'''
        if state == 0:
            registers.MEMORY.set_cache( False )
        elif state == 2:
            registers.MEMORY.set_cache( True )
    
    def set_pipeline_enable( self, state ):
        '''activates or disables pipeline'''
        if state == 0:
            self.pipeline.set_pipeline_status( False )
        elif state == 2:
            self.pipeline.set_pipeline_status( True )

    def load_program( self ):
        '''loads a binary file into main memory and updates gui to reflect changes'''
        initial_dir = os.path.dirname( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ) )
        file_name = filedialog.askopenfilename( initialdir = initial_dir, title = "Select Program" )
        b = None
        with open( file_name, 'rb' ) as f:
            b = bytearray( f.read() )
       
        mem_index = 0
        for i in range( 0, len( b ), 4 ):
            val = None
            if i + 4 > len(b):
                val = bytearray( b[ i: ] )
                pad_num = 4 - ( len( b ) - i ) 
                for _ in range( pad_num ):
                    val.append( 0 ) 
                val = bytes( val )
            else:
                val = bytes( b[ i: i + 4 ] )
           
            # put value in RAM
            registers.MEMORY.next_layer.mem[ mem_index // 4 ][ mem_index % 4 ] = val
            mem_index += 1

        # refresh gui with program 
        self.index_changed_memCombo( self.memCombo.currentIndex() )
        self.InstrView.setModel( view_models.InstrModel( dissassemble( file_name ) ) )

def main():
    app = QApplication(sys.argv)
    sim = Simulator()
    # hide tkinter root window
    root = tkinter.Tk()
    root.withdraw()
    sim.show()
    app.exec_()

if __name__ == '__main__':
    main()
