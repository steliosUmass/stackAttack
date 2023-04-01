from enum import Enum
from memory import Users, MemoryState
import registers 

class Op( Enum ):
    PUSH_VAL = 0
    DUP = 2
    LDR_32 = 3
    STR_32 = 4
    PUSH = 9
    POP = 10
    JMP_IF_1 = 12
    ADD = 16
    EQ = 25
    NOOP = 48 


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
    if op in ( Op.PUSH_VAL, Op.DUP ):
        result_val = operand_1
    elif op == Op.ADD:
        result_val = operand_1 + operand_2
    elif op == Op.EQ:
        result_val = 1 if operand_1 == operand_2 else 0
    elif op == Op.PUSH:
        registers.STACK.push( registers.PUSH )
    elif op == Op.POP:
        registers.STACK.pop()
    if result_val != None:
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
    squash = False
    if op == Op.JMP_IF_1:
        if condition is not None and condition == 1:
            print('here')
            registers.PC = address
            registers.INSTR_OFFSET = instr_offset
            squash = True
    return squash


def mem_op( op, address ):
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

