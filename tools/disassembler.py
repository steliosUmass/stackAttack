import pickle 
import json
import sys
import os 

def dissassemble( file_name ):
    instr_mapping = None
    with open( os.path.join( os.path.dirname(  os.path.realpath( __file__ ) ), 'instr_mapping.json' ), 'r' ) as f:
        instr_mapping = { v:k for k, v in json.load( f ).items() }
    
    instr_list = []
    b = None
    with open( file_name, 'rb' ) as f:
            b = pickle.load( f )
  
    b_arr = b[0]
    for i in range( len( b_arr ) ):
        val = b_arr[ i ]
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

if __name__ == '__main__':
    print( dissassemble( sys.argv[1] ) )
