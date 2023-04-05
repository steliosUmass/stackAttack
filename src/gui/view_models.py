# got this from https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys
import os

# Add pipeline directory to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'pipeline' ) )

import registers

class RamModel( QtCore.QAbstractTableModel ):
    def __init__(self, data):
        super(RamModel, self).__init__()
        self._data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()].hex()
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
                return 'Line ' + str(section)

class CacheModel( QtCore.QAbstractTableModel ):
    def __init__(self, tag, data, valid ):
        super(CacheModel, self).__init__()
        self._data = []
        for i, val in enumerate( data ):
            self._data.append( [ tag[ i ] ] + val + [ valid[ i ] ] )
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            val = self._data[index.row()][index.column()]
            if isinstance( val, bytes ):
                return val.hex()
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
    def __init__(self, pc, instr_offset, link, push, pop, cycle ):
        super(RegisterModel, self).__init__()
        self._data = [ 'PC: %d' % pc, ' INSTR_OFFSET: %d' % instr_offset, 
                'LINK: %d' % link, 'PUSH: {}'.format( push.to_bytes( 16, 'big' ).hex() ), 
                'POP: {}'.format( pop.to_bytes( 16, 'big' ).hex() ), '-'*20, 'Cycle: %d' % cycle ]
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
    
class InstrModel( QtCore.QAbstractListModel ):
    def __init__(self, data ):
        super(InstrModel, self).__init__()
        self._data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
    
class StackModel( QtCore.QAbstractListModel  ):
    def __init__(self, data ):
        super(StackModel, self).__init__()
        self._data = data
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str( self._data[index.row()] )
    
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
