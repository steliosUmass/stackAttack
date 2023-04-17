import registers

def POP_2(curr_instr):
    curr_instr['Operand_1'] = registers.STACK.remove()
    curr_instr['Operand_2'] = registers.STACK.remove()
    return curr_instr


def POP_3(curr_instr):
    curr_instr['Operand_1'] = registers.STACK.remove()
    curr_instr['Operand_2'] = registers.STACK.remove()
    curr_instr['Operand_3'] = registers.STACK.remove()
    return curr_instr

def MEM_ACCESS(curr_instr):
    curr_instr['Address'] = registers.STACK.remove()
    return curr_instr

def JMP(curr_instr):
    curr_instr['Condition'] = registers.STACK.remove()
    curr_instr['Address'] = registers.STACK.remove()
    curr_instr['Instr_offset'] = registers.STACK.remove()
    return curr_instr

def JMP_NO_CON(curr_instr):
    curr_instr['Address'] = registers.STACK.remove()
    curr_instr['Instr_offset'] = registers.STACK.remove()
    return curr_instr


function_map = {
    "ADD": POP_2,
    "SUB": POP_2,
    "EQ": POP_2,
    "LT": POP_2,
    "L_SHIFT": POP_2,
    "LDR_32": MEM_ACCESS,
    "STR_32": MEM_ACCESS,
    "JMP": JMP_NO_CON,
    "JMP_IF_1": JMP,
    "JMP_IF_0": JMP,
}
