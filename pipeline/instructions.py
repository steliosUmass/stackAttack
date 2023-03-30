from enum import Enum

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

if __name__ == '__main__':
