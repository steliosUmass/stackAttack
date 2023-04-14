import sys
import os
import json
import pickle

# read mapping of instructions to bytes
instr_mapping = None
with open( os.path.join( os.path.dirname(  os.path.realpath( __file__ ) ), 'instr_mapping.json' ), 'r' ) as f:
        instr_mapping = json.loads( f.read() )

def parse_int( val ):
    if isinstance( val, int ): return val
    return int( val, 16 if "0x" in val else 10 )

def gen_type_0_ops( val, op ):
    ops = []
    if op in [ 'DUP', 'SWAP' ]:
        if val > 31:
            raise ValueError( 'cannot have value greater than 31 for DUP/SWAP' )
        ops = [ instr_mapping[ op ] + val ]
    elif op == 'PUSH_VAL':
        if val > 2**128:
            raise ValueError( 'cannot push value greater than 2**32 for PUSH_VAL' )

       
        # if val is zero, just return one push val
        if val == 0:
            ops.append( instr_mapping[ 'PUSH_VAL' ]  )
        else:

            # the way this works is that we push the integer value 5 bits at a time
            # then, the bits are shifted into the correct spot
            # if a previous push_val has been done, do an add to combine the two values together
            shift_amount = 27
            need_add = False
            mask = 2**31 + 2**30 + 2**29 + 2**28 + 2**27
            while mask > 0:
                temp = val & mask
                #print( 'temp', temp, 'mask', bin(mask), 'shift_amount', shift_amount )
                if temp != 0:
                    # generate approperate push_val and shift
                    if shift_amount > 0:
                        temp = temp >> shift_amount
                        ops.append( instr_mapping[ 'PUSH_VAL' ] + temp )
                        ops.append( instr_mapping[ 'PUSH_VAL' ] + shift_amount )
                        ops.append( instr_mapping[ 'L_SHIFT' ] )
                    else:
                        ops.append( instr_mapping[ 'PUSH_VAL' ] + temp )
                    if need_add:
                        ops.append( instr_mapping[ 'ADD' ] )
                    need_add = True

                # decrement mask and shift amount
                mask = mask >> 5
                shift_amount -= 5

    return ops

def main():
    addr = 0
    instr_counter = 0
    symbol_table = {}
    instr_bytes = bytearray()

    with open( os.path.join( os.path.dirname(  os.path.realpath( __file__ ) ), 'instr_mapping.json' ), 'r' ) as f:
        instr_mapping = json.loads( f.read() )

    # open file for first pass to fill symbol table
    with open( sys.argv[1], 'r') as f:
        for line in f.readlines():
            line = line.split()
            if len(line) == 0 or line[0] == '#':
                continue
            
            instr = line[0]
            

            if instr == '.VAR':
                symbol_table[ line[1] ] = parse_int( line[2] )
            elif instr == '.ADDR':
                addr = parse_int( line[1] )
                instr_counter = -1
            elif instr not in instr_mapping.keys() and '.' != instr[ 0 ]:
                instr = instr.strip( ':' )
                symbol_table[ instr ] = ( addr + instr_counter // 4,  instr_counter % 4 )
            
            instr_counter += 1
  
    prog_dict = {}
    addr = 0
    
    # open file to create ops
    with open( sys.argv[1], 'r') as f:
        for line in f.readlines():
            line = line.split()
            if len(line) == 0 or line[0] == '#':
                continue
           
            # if there is a label, remove from line
            if line[0].strip(':') in symbol_table.keys():
                line = line[1:]
           
            instr = line[0]
            val = line[1]
                    
            # check if value is in symbol table
            if val in symbol_table.keys():
                val = symbol_table[ val ]
            elif not isinstance( val, tuple ):
                val = parse_int( val )
                    

            if instr in instr_mapping.keys():
                ops = None
                instr_byte = instr_mapping[ instr ]

                # type 0 instructions
                if instr_byte < 2**7:
                    
                    # check if value is tuple and instr is push back.
                    # if thats the case generate two push val instructions 
                    # one that pushes PC and other that pushes offset
                    if isinstance( val, tuple ) and instr == 'PUSH_VAL':
                        ops = ( gen_type_0_ops( parse_int( val[ 1 ] ), 'PUSH_VAL' ) + 
                            gen_type_0_ops( parse_int( val[ 0 ] ), 'PUSH_VAL' ) )
                    else:
                        ops = gen_type_0_ops( val, instr )
                
                    for op in ops:
                        instr_bytes.append( op )
                else:              
                    instr_bytes.append( instr_byte )                
            
            elif instr == '.LOAD':
                instr_bytes = instr_bytes + val.to_bytes( ( val.bit_length() + 7 ) // 8,  'big' )

            elif instr == '.ADDR':
                # first save current instructions to load
                # make sure instruction byte array is atleast full word
                prog_dict[ addr ] = instr_bytes
                
                # change current address to load instr too
                # reset byte array
                addr = val
                instr_bytes = bytearray()
    
    # final save 
    prog_dict[ addr ] = instr_bytes
    prog_dict[ 'symbol_table' ] = symbol_table
    print( prog_dict ) 

    # write file
    with open( sys.argv[ 2 ], 'wb' ) as f:
        pickle.dump( prog_dict, f )





     
if __name__ == '__main__':
    main()
