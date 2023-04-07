import registers


def PUSH_1(curr_instr, operand_1):
    curr_instr['Operand_1'] = operand_1
    return curr_instr


def POP_1(curr_instr):
    curr_instr['Operand_1'] = registers.STACK.remove()
    return curr_instr


def POP_2(curr_instr):
    curr_instr['Operand_1'] = registers.STACK.remove()
    curr_instr['Operand_2'] = registers.STACK.remove()
    return curr_instr


def POP_3(curr_instr):
    curr_instr['Operand_1'] = registers.STACK.remove()
    curr_instr['Operand_2'] = registers.STACK.remove()
    curr_instr['Operand_3'] = registers.STACK.remove()
    return curr_instr


function_map = {
    "PUSH": PUSH_1,
    "ADD": POP_2,
    "SUB": POP_2,
    "EQ": POP_2
}
