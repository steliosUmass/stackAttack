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

import registers
from disassembler import dissassemble

class Simulator(QtWidgets.QMainWindow, sim_gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Simulator, self).__init__(parent)
        self.setupUi(self)

        # init combo box to choose between ram and cache
        self.memCombo.addItems( [ 'RAM', 'CACHE'] )

        # set check state for cache on and pipeline on
        self.cacheOn.setChecked( True )
        self.pipeOn.setChecked( True )

        # set listener for combo box between memory and cache ( and call it with index 0 )
        self.memCombo.currentIndexChanged.connect( self.index_changed_memCombo )
        self.index_changed_memCombo( 0 )

        # init register table
        self.regView.setModel( view_models.RegisterModel( registers.PC, registers.INSTR_OFFSET, registers.LINK, registers.PUSH, registers.POP ) )

        # add listener to load program
        self.LoadButton.clicked.connect( self.load_program )           
    
    def index_changed_memCombo( self, index ):
        if index == 0:
            # show ram
            self.memTable.setModel( view_models.RamModel( registers.MEMORY.next_layer.mem ) )
        elif index == 1:
            # show cache
            self.memTable.setModel( view_models.CacheModel( registers.MEMORY.tag, registers.MEMORY.mem, registers.MEMORY.valid ) )

    def load_program( self ):
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
    root = tkinter.Tk()
    root.withdraw()
    sim.show()
    app.exec_()

if __name__ == '__main__':
    main()
