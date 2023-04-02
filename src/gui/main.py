# got example from https://pythonbasics.org/qt-designer-python/

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import view_models
import sim_gui
import sys
import os

# Add pipeline directory to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'pipeline' ) )
import registers

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
            
    def index_changed_memCombo( self, index ):
        if index == 0:
            # show ram ( only first 200 lines for now )
            self.memTable.setModel( view_models.RamModel( registers.MEMORY.next_layer.mem ) )
        elif index == 1:
            # show cache
            self.memTable.setModel( view_models.CacheModel( registers.MEMORY.tag, registers.MEMORY.mem, registers.MEMORY.valid ) )


def main():
    app = QApplication(sys.argv)
    sim = Simulator()
    sim.show()
    app.exec_()

if __name__ == '__main__':
    main()