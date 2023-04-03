
def dissassemble( file_name ):
    instr_mapping = {
            0: 'PUSH_VAL',
            2**6: 'DUP',
            2**7: 'LDR_32',
            2**7 + 1: 'STR_32',
            2**7 + 6: 'PUSH',
            2**7 + 7: 'POP',
            2**7 + 12: 'JMP_IF_1',
            2**7 + 13: 'JMP_IF_0',
            2**7  + 16: 'ADD',
            2**7 + 25: 'EQ',
            2**7 + 48: 'NOOP',
            2**7 + 49: 'HALT'
    }
   
    instr_list = []
    b = None
    with open( file_name, 'rb' ) as f:
            b = bytearray( f.read() )
   
    for i in range( len( b ) ):
        val = b[ i ]
        # if type 0, extract literal
        if val < 2**7:
            instr = instr_mapping[ val & 224 ]
            literal = val & 31
            if instr == 'PUSH_VAL':
                instr_list.append( '{} {}'.format( instr , str( literal ) ))

            else:
                instr_list.append( instr )
        else:
            instr_list.append( instr_mapping[ val ] )
            
    return instr_list
