import sys
import os

# Add instruction object to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'src', 'pipeline' ) )
from instructions import Op

instr_mapping = {
        Op.PUSH_VAL: 0,
        Op.DUP: 2**6,
        Op.LDR_32: 2**7,
        Op.STR_32: 2**7 + 1,
        Op.PUSH: 2**7 + 6,
        Op.POP :2**7 + 7,
        Op.JMP_IF_1: 2**7 + 9,
        Op.JMP_IF_0: 2**7 + 10,
        Op.ADD: 2**7  + 13,
        Op.EQ: 2**7 + 22,
        Op.NOOP: 2**7 + 45,
        Op.HALT: 2**7 + 46
}

program = [
        instr_mapping[ Op.PUSH_VAL ] + 7,
        instr_mapping[ Op.POP ],
        instr_mapping[ Op.PUSH_VAL ] + 31,
        instr_mapping[ Op.STR_32 ],
        instr_mapping[ Op.PUSH_VAL ] + 0,
        instr_mapping[ Op.PUSH_VAL ] + 1,
        instr_mapping[ Op.PUSH_VAL ] + 31,
        instr_mapping[ Op.LDR_32 ],
        instr_mapping[ Op.PUSH ],
        instr_mapping[ Op.PUSH_VAL ] + 1,
        instr_mapping[ Op.ADD],
        instr_mapping[ Op.DUP ],
        instr_mapping[ Op.POP ],
        instr_mapping[ Op.PUSH_VAL ] + 31,
        instr_mapping[ Op.STR_32 ],
        instr_mapping[ Op.PUSH_VAL ] + 10,
        instr_mapping[ Op.EQ ],
        instr_mapping[ Op.JMP_IF_0 ],
        instr_mapping[ Op.HALT ]
]

b = bytearray()
file_to_write = 'simple_program.bin'

for instr in program:
    b.append( instr )
b = bytes( b )

with open( file_to_write, 'wb' ) as f:
    f.write( b )
