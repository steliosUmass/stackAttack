# got example from https://pythonbasics.org/qt-designer-python/

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from tkinter import filedialog
import tkinter 
import view_models
import sim_gui
import sys
import os
import pickle
import re

# Add pipeline directory to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'pipeline' ) )
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ )  ) ) ), 'tools' ) )

from pipeline import PipeLine
import registers
from disassembler import dissassemble

class Simulator(QtWidgets.QMainWindow, sim_gui.Ui_simulator):
    def __init__(self, parent=None):
        super(Simulator, self).__init__(parent)
        self.setupUi(self)
        self.instr_offset = 0
        self.current_high_lighted_instr = False 
        # array of break points for program and symbol table
        self.breakpoints = []  
        self.symbol_table = {}

        # current address that mem should be pointing to
        self.current_mem_addr = 0
        
        #  add signal to change view of memory
        self.addrGo.clicked.connect( self.change_addr_view )
        
        # init combo box to choose between ram and cache
        self.memCombo.addItems( [ 'RAM', 'CACHE'] )

        # init combo box to different format representations
        self.memRepCombo.addItems( ['hex', 'binary', 'decimal' ] )
        self.regCombo.addItems( ['hex', 'binary', 'decimal' ] )
        self.stackComboBox.addItems( ['hex', 'binary', 'decimal' ] )

        # add signal to change table based on rep
        self.memRepCombo.currentIndexChanged.connect( lambda _: self.index_changed_memCombo( self.memCombo.currentIndex() ) )
        self.regCombo.currentIndexChanged.connect( lambda _:  ( self.regView.setModel( view_models.RegisterModel( 
                registers.PC, registers.INSTR_OFFSET, registers.LINK, registers.PUSH, registers.POP, self.regCombo.currentText() ) ) ) )
        self.stackComboBox.currentIndexChanged.connect( self.update_stack )

        
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
            registers.PC, registers.INSTR_OFFSET, registers.LINK, registers.PUSH, registers.POP ) )

        # add signal to load program
        self.LoadButton.clicked.connect( self.load_program )           

        # create pipeline object to controll simulation
        self.pipeline = PipeLine( self.breakpoints )

        # add signal for running sim
        self.runButton.clicked.connect( self.run )

        # add signal for step sim
        self.stepButton.clicked.connect( self.step )

        # update pipeline status
        self.fetchView.setModel( view_models.PipeLineModel( self.pipeline.fetch.get_state() ) )
        self.decodeView.setModel( view_models.PipeLineModel( self.pipeline.decode.get_state() ) )
        self.executeView.setModel( view_models.PipeLineModel( self.pipeline.execute.get_state() ) )

        # set signal for breakpoint set
        self.breakSet.clicked.connect( self.set_break_point )
        self.listBreakPoints.itemDoubleClicked.connect( self.delete_break_point )
        
        # set button to clear cache
        self.clearCacheButton.clicked.connect( self.clear_cache )

        # set running time info
        hit_percent = 'Cache Hit 0%' 
        running_info = [ f"Cycles: { self.pipeline.cycle }", hit_percent ]
        self.infoListView.setModel( view_models.BasicModel( running_info ) ) 

    def clear_cache( self ):
        registers.MEMORY.clear_cache()
        # update memory
        self.index_changed_memCombo( self.memCombo.currentIndex() )

    def delete_break_point( self, item ):
        _, pc, _, offset = item.text().split()
        self.breakpoints.remove( [ int( pc ), int( offset ) ] )
        self.listBreakPoints.takeItem( self.listBreakPoints.row( item ) )
        
    def set_break_point( self ):
        line_break = self.lineEditBreakPoint.text().split(',')
        if len( line_break ) != 2:
            print('ERROR setting break point')
        else:
            # append if breakpoint doesn't exist
            pc, offset =  [ int( x ) for x in line_break ]
            if [ pc, offset ] not in self.breakpoints:
                self.breakpoints.append( [ pc, offset ] )
                # add item to breakpoint list
                self.listBreakPoints.addItem( 'PC: {} OFFSET: {}'.format( line_break[ 0 ], line_break[ 1 ] ) )

    def change_addr_view( self ):
        self.current_mem_addr = int( self.lineEditAddr.text().strip() )
        self.index_changed_memCombo( self.memCombo.currentIndex() )
        
        
        self.InstrView.clear()
        addr = self.current_mem_addr // 4
        end_addr = addr + 1  if addr + 1 < len( registers.MEMORY.next_layer.mem ) else len( registers.MEMORY.next_layer.mem ) 
        defs, instrs = dissassemble( b''.join( 
            [ l for sublist in registers.MEMORY.next_layer.mem[ addr: end_addr ] for l in sublist ] ), self.symbol_table, addr * 16  )
        spacing =  ['',''] if len( defs ) > 0 else []      
        self.instr_index_offset = len( spacing ) + len( defs )
        self.InstrView.addItems( defs + spacing + instrs )
        
        #self.instr_offset = 0
        ## select instr if shown
        #if ( self.current_mem_addr // 4 )  * 16 <= registers.PC * 4 + registers.INSTR_OFFSET < ( self.current_mem_addr // 4 + 1 ) * 16:
        #    # get offset of current instruction based on PC
        #    for i in range(  self.instr_index_offset, self.instr_index_offset +  ( registers.PC * 4 + registers.INSTR_OFFSET ) - ( self.current_mem_addr // 4  * 16 ) ):
        #        print( self.InstrView.item( i ).text() )
        #        if re.match('PUSH_VAL [a-zA-Z]+', self.InstrView.item( i ).text() ) is not None:
        #            self.instr_offset -= 1
        #    print( self.instr_offset )
        #    self.InstrView.setCurrentRow( self.instr_index_offset +  ( registers.PC * 4 + registers.INSTR_OFFSET ) - ( self.current_mem_addr // 4  * 16 ) + self.instr_offset )

    def update_stack( self ):
        # update stack
        stack_list = registers.STACK.stack[ : registers.STACK.top_index + 1 ]
        self.stackView.setModel( view_models.StackModel( stack_list[ : : -1 ], val_format=self.stackComboBox.currentText() ) )


    def update_gui( self ):
        '''updates the gui with the current state of the simulator'''
        # update memory
        self.index_changed_memCombo( self.memCombo.currentIndex() )
       
        self.update_stack()

        # update registers 
        self.regView.setModel( view_models.RegisterModel( 
            registers.PC, registers.INSTR_OFFSET, registers.LINK, registers.PUSH, registers.POP, self.regCombo.currentText() ) )

        # update pipeline status
        self.fetchView.setModel( view_models.PipeLineModel( self.pipeline.fetch.get_state() ) )
        self.decodeView.setModel( view_models.PipeLineModel( self.pipeline.decode.get_state() ) )
        self.executeView.setModel( view_models.PipeLineModel( self.pipeline.execute.get_state() ) )
        
        # set running time info
        hit_percent = ( 'Cache Hit 0%' if registers.MEMORY.num_reads == 0 
            else f"Cache Hit { registers.MEMORY.num_hits / registers.MEMORY.num_reads * 100:.2f}%" )
        running_info = [ f"Cycles: { self.pipeline.cycle }", hit_percent ]
        self.infoListView.setModel( view_models.BasicModel( running_info ) ) 


        # logic for highlighting current instr pointed to
        # will fix if have extra time 
        # select instr if shown
        #if ( self.current_mem_addr // 4 )  * 16 <= registers.PC * 4 + registers.INSTR_OFFSET < ( self.current_mem_addr // 4 + 1 ) * 16 + self.instr_offset:
        #    # calc instruction offset if previous instr wasn't highlighted
        #    if not self.current_high_lighted_instr:
        #        for i in range(  self.instr_index_offset, self.instr_index_offset +  ( registers.PC * 4 + registers.INSTR_OFFSET ) - ( self.current_mem_addr // 4  * 16 ) ):
        #            print( self.InstrView.item( i ).text() )
        #            if re.match('PUSH_VAL [a-zA-Z]+', self.InstrView.item( i ).text() ) is not None:
        #                self.instr_offset -= 1
        #    
        #    self.current_high_lighted_instr = True
        #    self.InstrView.setCurrentRow( self.instr_index_offset +  ( registers.PC * 4 + registers.INSTR_OFFSET ) - ( self.current_mem_addr // 4  * 16 ) + self.instr_offset )
        #    i = self.instr_index_offset +  ( registers.PC * 4 + registers.INSTR_OFFSET ) - ( self.current_mem_addr // 4  * 16 ) + self.instr_offset 
        #    print( self.InstrView.item( i ).text() )
        #    print( self.instr_offset )
        #    
        #    # see if current instruction is "PUSH_VAL LABEL", if so decrement offset
        #    if re.match('PUSH_VAL [a-zA-Z]+', self.InstrView.item( 
        #            self.instr_index_offset +  ( registers.PC * 4 + registers.INSTR_OFFSET ) - ( self.current_mem_addr // 4  * 16 ) ).text() ):
        #        self.instr_offset -= 1

        #else:
        #    self.InstrView.clearSelection()
        #    self.current_high_lighted_instr = False
        #    self.instr_offset = 0

    def step( self ):
        '''step through one cycle'''
        self.pipeline.step( )
        self.update_gui( ) 
    
    def run( self ):
        '''runs simulation untill halt instr is reached'''
        self.pipeline.run( )
        self.update_gui( ) 

    def index_changed_memCombo( self, index ):
        '''updates the mem table to show either cache or ram based on comboBox index'''
        
        # if in binary mode, set to resize contents
        if self.memRepCombo.currentText() == 'binary':
            self.memTable.horizontalHeader().setSectionResizeMode( QtWidgets.QHeaderView.ResizeToContents)
        else:
            self.memTable.horizontalHeader().setSectionResizeMode( QtWidgets.QHeaderView.Stretch )

        if index == 0:
            # show ram
            addr = self.current_mem_addr // 4
            end_addr = addr + 20 if addr + 20 < len( registers.MEMORY.next_layer.mem ) else len( registers.MEMORY.next_layer.mem ) 
            self.memTable.setModel( view_models.RamModel( registers.MEMORY.next_layer.mem[ addr: end_addr ],
                self.current_mem_addr, val_format=self.memRepCombo.currentText() ) )
        elif index == 1:
            # show cache
            self.memTable.setModel( view_models.CacheModel( registers.MEMORY.tag, registers.MEMORY.mem, registers.MEMORY.valid,
                val_format=self.memRepCombo.currentText()) )

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
        prog = None
        with open( file_name, 'rb' ) as f:
            prog = pickle.load( f )
        
        # for each item in dict
        # go through
        for addr, b in prog.items():
            if addr == 'symbol_table':
                self.symbol_table = b
            else:
                mem_index = 0
                for i in range( 0, len( b ), 4 ):
                    val = None
                    # pad with zero if less than 4
                    if i + 4 > len(b):
                        val = bytearray( b[ i: ] )
                        pad_num = 4 - ( len( b ) - i ) 
                        for _ in range( pad_num ):
                            val.append( 0 ) 
                        val = bytes( val )
                    else:
                        val = bytes( b[ i: i + 4 ] )
                   
                    # put value in RAM
                    registers.MEMORY.next_layer.mem[ ( addr + mem_index ) // 4 ][ ( addr + mem_index ) % 4 ] = val
                    mem_index += 1

        # refresh gui with program 
        self.index_changed_memCombo( self.memCombo.currentIndex() )

        # print out line of instruction
        addr = self.current_mem_addr // 4
        end_addr = addr + 1  if addr + 1 < len( registers.MEMORY.next_layer.mem ) else len( registers.MEMORY.next_layer.mem ) 
        defs, instrs = dissassemble( b''.join( 
            [ l for sublist in registers.MEMORY.next_layer.mem[ addr: end_addr ] for l in sublist ] ), self.symbol_table, addr * 16  )
        spacing =  ['',''] if len( defs ) > 0 else []      
        self.instr_index_offset = len( spacing ) + len( defs )
        self.InstrView.addItems( defs + spacing + instrs )

        # select first row
        self.InstrView.setCurrentRow( self.instr_index_offset )

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
