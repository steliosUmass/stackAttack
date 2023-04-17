import sys
import os
import json
import pickle
import re

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
        ops = [ f"{ op } { val }" ]
    elif op == 'PUSH_VAL':
        if val > 2**128:
            raise ValueError( 'cannot push value greater than 2**32 for PUSH_VAL' )

       
        # if val fits in one push_val
        # just push one instr 
        if val < 32:
            ops.append( f"PUSH_VAL { val }" )
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
                        ops.append( f"PUSH_VAL { temp }" )
                        ops.append( f"PUSH_VAL { shift_amount }" )
                        ops.append( 'L_SHIFT' )
                    else:
                        ops.append( f"PUSH_VAL { temp }" )
                    if need_add:
                        ops.append( 'ADD' )
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

    prog_lines = []
    prog_index = 0
    
    # this dict keeps track of in index of lines that refernce 
    # branching labels 
    referenced_labels = {}
    label_definitons = []
    
    # in this first pass, we open the file
    # we expand push_val ops if needed
    # we add any .VAR variables to the symbol table
    # we add any labels to symbol table
    # we do NOT expand label push values 
    with open( sys.argv[1], 'r') as f:
        for line in f.readlines():
            line_split = line.split()
            if len(line_split) == 0 or line_split[0][0] == '#':
                continue
            
            instr = line_split[0]

            if instr == '.VAR':
                if instr in symbol_table.keys():
                    raise Exception( f"Error: Cannot declare variable \"{ instr }\" after reference" )
                symbol_table[ line_split[1] ] = parse_int( line_split[2] )
            elif instr == '.ADDR':
                val = line_split[1]
                if val in symbol_table.keys():
                    val = symbol_table[ val ]
                addr = parse_int( val )
                instr_counter = 0
                prog_lines.append( f".ADDR { val }" )
                prog_index += 1
            elif instr == '.LOAD':
                prog_lines.append( line )
            else:
                if instr not in instr_mapping.keys() and '.' != instr[ 0 ]:
                    # label definition found here
                    instr = instr.strip( ':' )
                    symbol_table[ instr ] = ( addr + prog_index // 4, prog_index % 4 )
                    label_definitons.append( instr )
                    line_split = line_split[ 1: ] 
                    line = ' '.join(  line_split )
                    instr = line_split[ 0 ]
                if len( line_split ) > 1:
                    
                    val = line_split[1]
                    # check if value is in symbol table
                    if val in symbol_table.keys():
                        val = symbol_table[ val ]
                    if isinstance( val, tuple ) or re.search('[a-zA-Z]', str( val ) ) is not None:
                        # this is a push_val branch
                        # assume this will only generate 2 instructions for now
                        prog_lines.append( line.strip( '\n' ) )
                        if line_split[ 1 ] not in referenced_labels.keys():
                            referenced_labels[ line_split[ 1 ] ] = []

                        referenced_labels[ line_split[ 1 ] ].append( prog_index )
                        prog_index += 2
                        continue
                    
                    elif re.match( '0x[a-fA-F0-9]+|[0-9]+', str( val ) ) is not None:
                        val = parse_int( val )
                    
                    ops = gen_type_0_ops( val, instr )
                    prog_index += len( ops )
                    prog_lines.extend( ops )
                else:
                    prog_lines.append( instr )
                    prog_index += 1

    # now we go through all the "PUSH_VAL branch" 
    # and we replace the label with PUSH_VAL OFFSET PUSH_VAL PC
    # we also check to see if the PC can fit in the 5 bit literal
    # if not we expand the operation and we need to modify the address 
    # of following labels
    # this process continues until things don't change

    num_pc_bits = {}
    ops_needed_for_push = {}
    # now, expand the values being pushed
    for label in label_definitons:
        num_pc_bits[ label ] = 5
        ops_needed_for_push[ label ] = 1
     
    did_change = True
    while did_change:
        did_change = False
        
        for label in label_definitons:
            pc = symbol_table[ label ][ 0 ] 
            # check if bit length cannot fit in currently allocated bit length
            if pc.bit_length() > num_pc_bits[ label ]:
                
                did_change = True
                # increment number of pc bits needed
                num_pc_bits[ label ] += 5
                # for new address, get number of ops needed to push pc
                ops_needed_for_push[ label ] = len( gen_type_0_ops( pc, 'PUSH_VAL' ) ) - ops_needed_for_push[ label ]


                # change symbol table value for each label
                for label_2 in label_definitons:
                    if label_2 == label:
                        continue
                    # check to see how many push_val operations are before label def
                    operations_before = 0
                    for ref in referenced_labels[ label ]:
                        print( label_2, ref, symbol_table[ label_2 ][ 0 ] * 4 + symbol_table[ label_2 ][ 1 ] )
                        if ref < symbol_table[ label_2 ][ 0 ] * 4 + symbol_table[ label_2 ][ 1 ]:
                            operations_before += 1
                            
                    # for each label def, add the number of additonal ops * operations_before to get new address
                    addr_label_2 = symbol_table[ label_2 ][ 0 ] * 4 + symbol_table[ label_2 ][ 1 ]
                    symbol_table[ label_2 ] = ( (  addr_label_2 + operations_before * ops_needed_for_push[ label ] ) // 4, 
                            ( addr_label_2 + operations_before * ops_needed_for_push[ label ] ) % 4 )

    prog_dict = {}
    instr_bytes = bytearray()
    addr = 0
    # open file to create ops
    for line in prog_lines:
        line_split = line.split()
        instr = line_split[0]
        
        if instr in instr_mapping.keys():
            ops = []
            if instr == 'PUSH_VAL' and line_split[ 1 ] in symbol_table.keys():
                # insert PUSH_VAL symbol table here
                ops = ( gen_type_0_ops( symbol_table[ line_split[ 1 ] ][ 1 ], instr ) +
                            gen_type_0_ops( symbol_table[ line_split[ 1 ]  ][ 0 ], instr ) )
            else:
                ops = [ line ]
            
            for op in ops:
                op_split = op.split()
                instr_byte = instr_mapping[ op_split[ 0 ] ]
                if len( op_split ) > 1:
                    instr_byte += parse_int( op_split[ 1 ] )
                instr_bytes.append( instr_byte )                
            
        elif instr == '.LOAD':
            for val in line_split[ 1: ]:
                if val in symbol_table.keys():
                    val = symbol_table[ val ]
            
                val = parse_int( val )
                instr_bytes.extend( val.to_bytes( 4, 'big' ) ) 
        
        elif instr == '.ADDR':
            # first save current instructions to load
            # make sure instruction byte array is atleast full word
            prog_dict[ addr ] = instr_bytes
            
            # change current address to load instr too
            # reset byte array
            # check if val is in symbol_table 
            val = line_split[ 1 ]
            if val in symbol_table.keys():
                val = symbol_table[ val ]

            val = parse_int( val )
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
