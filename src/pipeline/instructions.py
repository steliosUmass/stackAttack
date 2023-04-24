from enum import Enum
from memory import Users, MemoryState
import registers 

class Op( Enum ):
    PUSH_VAL = 0
    SWAP = 1
    DUP = 2
    LDR_32 = 3
    STR_32 = 4
    LDR_64 = 5
    STR_64 = 6
    LDR_128 = 7
    STR_128 = 8
    PUSH = 9
    POP = 10
    JMP = 11
    JMP_IF_1 = 12
    JMP_IF_0 = 13
    SR = 14
    RET = 15
    ADD = 16
    MUL = 17
    SUB = 18
    DIV = 19
    MOD = 20
    AND = 21
    OR = 22
    XOR = 23
    NOT = 24
    EQ = 25
    EQ_0 = 26
    GEQ = 27
    LEQ = 28
    GT = 29
    LT = 30
    R_SHIFT = 31
    L_SHIFT = 32
    NOOP = 48 
    HALT = 49


def alu_op( op,  operand_1, operand_2, operand_3 ):
    '''
    Does ALU operations
    
    Parameters
    ----------
    op:
        Op of instuction to execute
    operand_1:
        first operand from stack, None if not applicable 
    operand_2:
        second operand from stack, None if not applicable 
    operand_3: 
        third operand from stack, None if not applicable 

    '''
    result_val = None
    # modifiy operands to be 32 bit only
    if operand_1:
        operand_1 = operand_1 & 0xFFFFFFFF
    if operand_2:
        operand_2 = operand_2 & 0xFFFFFFFF
    if operand_3:
        operand_3 = operand_3 & 0xFFFFFFFF

    if op == Op.PUSH_VAL:
        result_val = operand_1
    elif op == Op.DUP:
        result_val = registers.STACK.stack[ registers.STACK.top_index - operand_1 ]
    elif op == Op.SWAP:
        ( registers.STACK.stack[ registers.STACK.top_index - operand_1 ],
            registers.STACK.stack[ registers.STACK.top_index  ] ) = ( registers.STACK.stack[ registers.STACK.top_index  ],
            registers.STACK.stack[ registers.STACK.top_index - operand_1 ] )
    elif op == Op.ADD:
        result_val = operand_1 + operand_2
    elif op == Op.SUB:
        result_val = operand_2 - operand_1
    elif op == Op.MUL:
        result_val = operand_1 * operand_2
    elif op == Op.DIV:
        result_val = operand_1 // operand_2 if operand_2 != 0 else 0
    elif op == Op.MOD:
        result_val = operand_1 % operand_2
    elif op == Op.AND:
        result_val = operand_1 & operand_2
    elif op == Op.OR:
        result_val = operand_1 | operand_2
    elif op == Op.XOR:
        result_val = operand_1 ^ operand_2
    elif op == Op.NOT:
        # invert by xor with 1
        result_val = operand_1 ^ 0xFFFFFFFF
    elif op == Op.EQ:
        result_val = 1 if operand_1 == operand_2 else 0
    elif op == Op.EQ_0:
        result_val = 0 if operand_1 == operand_2 else 1
    elif op == Op.GEQ:
        result_val = 1 if operand_1 >= operand_2 else 0
    elif op == Op.LEQ:
        result_val = 1 if operand_1 <= operand_2 else 0
    elif op == Op.GT:
        result_val = 1 if operand_1 > operand_2 else 0
    elif op == Op.LT:
        result_val = 1 if operand_1 < operand_2 else 0
    elif op == Op.PUSH:
        registers.STACK.push( registers.PUSH )
    elif op == Op.POP:
        registers.STACK.pop()
    elif op == Op.L_SHIFT:
        result_val = operand_2 << operand_1
    elif op == Op.R_SHIFT:
        result_val = operand_2 >> operand_1
    if result_val is not None:
        registers.STACK.push( result_val )

def branch_op( op, condition, address, instr_offset ):
    '''
    Checks branch condition, and updates PC + INSTR_OFFSET
    
    Parameters
    ----------
    op:
        Op of instuction to execute
    condition:
        condition value
    address:
        address of word to jump to
    instr_offset: 
        offset of instruction to start at

    Returns
    --------
    squash:
        bool indicating if earlier instuctions in the pipe should be squashed
    '''
    if condition:
        # get least sign bit only
        condition = condition & 1
    squash = False
    if op == Op.JMP_IF_1:
        if condition is not None and condition == 1:
            registers.PC = address
            registers.INSTR_OFFSET = instr_offset
            squash = True
    elif op == Op.JMP_IF_0:
       if condition is not None and condition == 0:
           registers.PC = address
           registers.INSTR_OFFSET = instr_offset
           squash = True
    elif op == Op.JMP:
           registers.PC = address
           registers.INSTR_OFFSET = instr_offset
           squash = True

    return squash


class MemoryExecuter():
    def __init__( self ):
        self.second_read = False
    
    def mem_op( self, op, address ):
        '''
        writes or reads value into memory
        
        Parameters
        ----------
        op:
            Op of instuction to execute
        address:
            memory address to read/write to
    
        Returns
        --------
        mem_status:
            status return by memory
        '''
        mem_status = None
        if op == Op.LDR_32:
            mem_status = registers.MEMORY.read( address, Users.MEMORY )
            if mem_status != MemoryState.BUSY:
                registers.PUSH = int.from_bytes( mem_status[ address % 4 ], "big")
        elif op == Op.STR_32:
            mem_status = registers.MEMORY.write( address, int( registers.POP & 2**32 - 1 ).to_bytes( 4, 'big' ), Users.MEMORY ) 
        elif op == Op.LDR_64:
            # if the second word we need is in the next line
            # read next line 
            mem_status = None
            if self.second_read:
                mem_status = registers.MEMORY.read( address + 1, Users.MEMORY )
            else:
                mem_status = registers.MEMORY.read( address, Users.MEMORY )
    
            if mem_status != MemoryState.BUSY:
                if self.second_read:
                    registers.PUSH += int.from_bytes( mem_status[ address % 4 ], "big")
                    self.second_read = False
                # are both words in same line?
                # if so we have both words
                elif address // 4 == ( address + 1 ) // 4:
                    registers.PUSH =  ( ( int.from_bytes( mem_status[ address % 4 ], "big") << 32 ) 
                        + int.from_bytes( mem_status[ ( address + 1 ) % 4 ], "big") )
                # else, just put what we have 
                else:
                    registers.PUSH =  ( int.from_bytes( mem_status[ address % 4 ], "big") << 32 ) 
                    self.second_read = True
                    mem_status = MemoryState.BUSY
        elif op == Op.STR_64:
            registers.MEMORY.write( address, int( ( registers.POP >> 32 ) & 0xFFFFFFFF ).to_bytes( 4, 'big' ), Users.MEMORY ) 
            mem_status = registers.MEMORY.write( address + 1, int( registers.POP & 0xFFFFFFFF ).to_bytes( 4, 'big' ), Users.MEMORY ) 

        elif op == Op.LDR_128:
            # if the second word we need is in the next line
            # read next line 
            mem_status = None
            if self.second_read:
                mem_status = registers.MEMORY.read( address + 4, Users.MEMORY )
            else:
                mem_status = registers.MEMORY.read( address, Users.MEMORY )
    
            if mem_status != MemoryState.BUSY:
                if self.second_read:
                    num_vals =  ( address + 4  ) % 4
                    for i in range( num_vals ):
                        registers.PUSH += int.from_bytes( mem_status[ i ], "big") << ( 32 * ( num_vals - 1 - i ) )
                    self.second_read = False
                # else, just put what we have 
                else: 
                    registers.PUSH = 0
                    num_vals =  address % 4
                    self.second_read = num_vals != 0
                    for i in range( num_vals, 4 ):
                        registers.PUSH += int.from_bytes( mem_status[ i ], "big") << ( 96 - ( 32*( i - num_vals )  ) )
                    
                    mem_status = MemoryState.BUSY if self.second_read else mem_status
        elif op == Op.STR_128:
            registers.MEMORY.write( address, int( ( registers.POP >> 96 ) & 0xFFFFFFFF ).to_bytes( 4, 'big' ), Users.MEMORY ) 
            registers.MEMORY.write( address + 1, int( ( registers.POP >> 64 ) & 0xFFFFFFFF ).to_bytes( 4, 'big' ), Users.MEMORY ) 
            registers.MEMORY.write( address + 2, int( ( registers.POP >> 32 ) & 0xFFFFFFFF ).to_bytes( 4, 'big' ), Users.MEMORY ) 
            mem_status = registers.MEMORY.write( address + 3, int( registers.POP & 0xFFFFFFFF ).to_bytes( 4, 'big' ), Users.MEMORY ) 

        return mem_status

if __name__ == '__main__':
    # test ALU

    # test push_val
    op_1 = 3
    op_2 = 5
    alu_op( Op.PUSH_VAL, op_1, op_2, None )
    print( 'Push_val:', registers.STACK )
    # test DUP
    alu_op( Op.DUP, op_1, op_2, None )
    print( 'DUP:',  registers.STACK )
    # test add
    alu_op( Op.ADD, op_1, op_2, None )
    print( 'ADD:',  registers.STACK )
    # test EQ
    alu_op( Op.EQ, op_1, op_2, None )
    print( 'EQ:',  registers.STACK )
    # test push
    registers.PUSH = 23
    alu_op( Op.PUSH, op_1, op_2, None ) 
    print( 'PUSH:', registers.STACK )
    # test pop
    alu_op( Op.POP, op_1, op_2, None )
    print( 'POP:', registers.STACK, registers.POP )


    # TEST BRANCHING 
    branch_op( Op.JMP_if_1, 1, 68, 2 )
    print('PC', registers.PC )
    print('INSTR_OFFSET', registers.INSTR_OFFSET )

    # test mem instructions
    mem_status = MemoryState.BUSY

    while mem_status == MemoryState.BUSY:
        mem_status = mem_op( Op.STR_32, 100 )   
    print( registers.MEMORY.next_layer.mem[ 25 ] )
    while mem_status == MemoryState.BUSY:
        mem_status = mem_op( Op.LDR_32, 100 )
    print( registers.PUSH )

    # test mem read instructions
    mem_status = MemoryState.BUSY

    while mem_status == MemoryState.BUSY:
        mem_status = mem_op( Op.STR_32, 100 )   
    print( registers.MEMORY.next_layer.mem[ 25 ] )
    while mem_status == MemoryState.BUSY:
        mem_status = mem_op( Op.LDR_32, 100 )
    print( registers.PUSH )
    
    # test mem read in cache instructions
    mem_status = MemoryState.BUSY

    while mem_status == MemoryState.BUSY:
        mem_status = mem_op( Op.STR_32, 100 )   
    print( registers.MEMORY.next_layer.mem[ 25 ] )
    while mem_status == MemoryState.BUSY:
        mem_status = mem_op( Op.LDR_32, 100 )
    print( registers.PUSH )

