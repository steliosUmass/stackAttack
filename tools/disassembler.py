import pickle 
import json
import sys
import os 

def dissassemble( instr_bytes, symbol_table, base_addr=0 ):
    instr_mapping = None
    with open( os.path.join( os.path.dirname(  os.path.realpath( __file__ ) ), 'instr_mapping.json' ), 'r' ) as f:
        instr_mapping = { v:k for k, v in json.load( f ).items() }
  
    defs_used = []
    instr_list = []
    addr = base_addr
    for i in range( len( instr_bytes ) ):
        val = instr_bytes[ i ]
        # if type 0, extract literal
        if val < 2**7:
            op_code = val & 224 
            if op_code not in instr_mapping.keys():
                instr_list.append( '-' )
            else:
                instr = instr_mapping[ op_code ]
                literal = val & 31

                # check if this line had a label or 
                # literal is a variable
                # Also check if the last two instr where push_val
                # if thats the case, could replace them with a "PUSH_VAL LABEL"
                pc = None
                offset = None

                if len( instr_list ) > 0 and instr_list[ -1 ].startswith( 'PUSH_VAL' ) and instr ==  'PUSH_VAL':
                    pc = literal
                    val = instr_list[ -1 ].split()[ -1 ]
                    if val in symbol_table.keys():
                        offset = symbol_table[ val ]
                    else:
                        if instr_list[ -1 ].split()[ -1 ].isdigit():
                            offset = int( instr_list[ -1 ].split()[ -1 ] )
                
                variable = None
                label = ''
                for var, val in symbol_table.items():
                    if pc != None and ( pc, offset ) == val:
                       prev_instr = instr_list[ -1 ].split()
                       prev_instr[ -1 ] = var + ' ( OFFSET )'
                       instr_list[ -1 ] = ' '.join( prev_instr )
                       variable = var + ' ( PC )'
                       if f"{var} = PC:{ val[0] } OFFSET:{ val[1] }" not in defs_used:
                          defs_used.append( f"{var} = PC:{ val[0] } OFFSET:{ val[1] }")
                    if variable == None and literal == val:
                        variable = var
                        if f"{var} = {val}" not in defs_used:
                            defs_used.append( f"{var} = {val}")
                    if ( addr // 4, addr % 4 ) == val:
                        label = f"{var}: "
                        
                instr_list.append( '{}{} {}'.format( label, instr , variable if variable != None else str( literal ) ))

        else:
            if val not in instr_mapping.keys():
                instr_list.append( '-' )
            else:
                # check for label
                label=''
                for var, value in symbol_table.items():
                    if ( addr // 4, addr % 4 ) == value:
                        label = f"{var}: "
                        
                instr_list.append( '{}{}'.format( label, instr_mapping[ val ] ) )
        addr += 1
            
    return defs_used, instr_list

if __name__ == '__main__':
    prog = None
    with open( sys.argv[ 1 ], 'rb' ) as f:
            prog = pickle.load( f )
    for addr, b in prog.items():
        if addr == 'symbol_table':
            continue
        print( 'ADDR: ', addr )
        print( dissassemble( b , prog['symbol_table' ] , base_addr=addr )[ 1 ])
