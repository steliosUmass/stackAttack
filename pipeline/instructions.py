from enum import Enum
import 
class Op( Enum ):
    NOOP = 48 
    PUSH_VAL = 0
    DUP = 2
    LDR_32 = 3
    STR_32 = 4
    PUSH = 9
    POP = 10
    JMP_if_1 = 12
    ADD = 16
    EQ = 25

def alu_op( op,  operand_1, operand_2, operand_3 ):
    result_val = None
    if op in ( Op.PUSH_VAL, Op.DUP ):
        result_val = operand_1
    elif op == Op.ADD:
        result_val = operand_1 + operand_2
    elif op == Op.EQ:
        result_val = 1 if operand_1 == operand_2 else 0

