# got this from https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys
import os

# Add pipeline directory to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'pipeline' ) )

import registers

class RamModel( QtCore.QAbstractTableModel ):
    def __init__(self, data, base_addr, val_format='hex' ):
        super(RamModel, self).__init__()
        self._data = data
        self.val_format = val_format
        self.base_addr = base_addr
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            if self.val_format == 'hex':
                return self._data[index.row()][index.column()].hex()
            elif self.val_format == 'binary':
                return f"{ int.from_bytes( self._data[index.row()][index.column()], 'big' ) :032b}"
            elif self.val_format == 'decimal':
                return str( int.from_bytes( self._data[index.row()][index.column()], 'big' ) )
        elif role == Qt.BackgroundRole:
            if index.row() * 4 + index.column() == registers.PC:
                return QtGui.QColor.fromRgb( 255, 255, 224, alpha=.8 )

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return 'Word ' + str(section)
            if orientation == Qt.Vertical:
                return 'Line ' + str( self.base_addr // 4 + section)

class CacheModel( QtCore.QAbstractTableModel ):
    def __init__(self, tag, data, valid, val_format='hex'):
        super(CacheModel, self).__init__()
        self._data = []
        for i, val in enumerate( data ):
            self._data.append( [ tag[ i ] ] + val + [ valid[ i ] ] )
        self.val_format = val_format
   
    def data(self, index, role):
        if role == Qt.DisplayRole:
            val = self._data[index.row()][index.column()]
            if isinstance( val, bytes ):
                if self.val_format == 'hex':
                    return self._data[index.row()][index.column()].hex()
                elif self.val_format == 'binary':
                    size = len( self._data[index.row()][index.column()] )
                    return f"{ int.from_bytes( self._data[index.row()][index.column()], 'big' ) :0{size * 8 }b}"
                elif self.val_format == 'decimal':
                    return str( int.from_bytes( self._data[index.row()][index.column()], 'big' ) )
            elif isinstance( val, bool ):
                return '1' if val else '0'
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
    
    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        # section is the index of the column/row
        col_headers = [ 'Tag', 'Word 0', 'Word 1', 'Word 2', 'Word 3', 'Valid' ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return col_headers[section]

            if orientation == Qt.Vertical:
                return 'Line ' + str(section)

class RegisterModel( QtCore.QAbstractListModel ):
    def __init__(self, pc, instr_offset, link, push, pop, val_format='hex' ):
        super(RegisterModel, self).__init__()
        self._data = []
        if val_format == 'hex':
            self._data = [ 'PC: %s' % pc.to_bytes( 2,'big' ).hex(), ' INSTR_OFFSET: %s' % instr_offset.to_bytes(1, 'big' ). hex(), 
                    'LINK: %s' % link.to_bytes(2, 'big' ).hex(), 'PUSH: {}'.format( push.to_bytes( 16, 'big' ).hex() ), 
                    'POP: {}'.format( pop.to_bytes( 16, 'big' ).hex()) ]
        elif val_format == 'decimal':
            self._data = [ 'PC: %d' % pc, ' INSTR_OFFSET: %d' % instr_offset, 
                    'LINK: %d' % link, 'PUSH: {}'.format( push ), 
                    'POP: {}'.format( pop )  ]
        elif val_format == 'binary':
            self._data = [ f"PC: {pc:016b}", f"INSTR_OFFSET: {instr_offset:02b}", 
                    f"LINK: {link:016b}", f"PUSH: {push:0128b}", f"POP: {pop:0128b}" ]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
    
class BasicModel( QtCore.QAbstractListModel ):
    def __init__(self, data ):
        super(BasicModel, self).__init__()
        self._data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
    
class StackModel( QtCore.QAbstractListModel  ):
    def __init__(self, data, val_format='hex' ):
        super(StackModel, self).__init__()
        self._data = data
        self.val_format = val_format
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            if self.val_format == 'hex':
                 return self._data[index.row()].to_bytes( 16, 'big').hex()
            elif self.val_format == 'binary':
                 return f"{ self._data[index.row()]:0128b}"
            elif self.val_format == 'decimal':
                return str( self._data[index.row()] )
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

class PipeLineModel( QtCore.QAbstractListModel  ):
    def __init__(self, data ):
        super(PipeLineModel, self).__init__()
        self._data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[ index.row() ] 
    def rowCount(self, index):
        return len( self._data )
