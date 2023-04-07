import registers


def POP_1(curr_instr):
    registers.STACK.pop()
    curr_instr['Operand_1'] = registers.POP
    return curr_instr


def POP_2(curr_instr):
    registers.STACK.pop()
    curr_instr['Operand_1'] = registers.POP
    registers.STACK.pop()
    curr_instr['Operand_2'] = registers.POP
    return curr_instr


def POP_3(curr_instr):
    registers.STACK.pop()
    curr_instr['Operand_1'] = registers.POP
    registers.STACK.pop()
    curr_instr['Operand_2'] = registers.POP
    registers.STACK.pop()
    curr_instr['Operand_3'] = registers.POP
    return curr_instr


function_map = {
    "ADD": POP_2,
    "SUB": POP_2,
    "EQ": POP_2
}
