import registers


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

def SR(curr_instr):
    curr_instr['Address'] = registers.STACK.remove()
    curr_instr['Instr_offset'] = registers.STACK.remove()

    # set link register here
    registers.LINK = registers.PC << 2
    registers.LINK += registers.INSTR_OFFSET
    return curr_instr

def RET(curr_instr):
    curr_instr['Address'] = None
    curr_instr['Instr_offset'] = None
    return curr_instr


function_map = {
    "ADD": POP_2,
    "MUL": POP_2,
    "SUB": POP_2,
    "DIV": POP_2,
    "MOD": POP_2,
    "AND": POP_2,
    "OR": POP_2,
    "XOR": POP_2,
    "NOT": POP_1,
    "EQ": POP_2,
    "EQ_0": POP_2,
    "GEQ": POP_2,
    "LEQ": POP_2,
    "GT": POP_2,
    "LT": POP_2,
    "L_SHIFT": POP_2,
    "R_SHIFT": POP_2,
    "LDR_32": MEM_ACCESS,
    "LDR_64": MEM_ACCESS,
    "LDR_128": MEM_ACCESS,
    "STR_32": MEM_ACCESS,
    "STR_64": MEM_ACCESS,
    "STR_128": MEM_ACCESS,
    "JMP": JMP_NO_CON,
    "JMP_IF_1": JMP,
    "JMP_IF_0": JMP,
    "SR": SR,
    "RET": RET,
    "GCD" : POP_2,
    "LCM" : POP_2,
    "RABIN" : POP_1,
    "MOD_ADD" : POP_3,
    "MOD_MUL" : POP_3,
    "MOD_INV" : POP_2,
    "DH" : POP_3,
    "RSA" : POP_3,
    "AESE" : POP_2,
    "AESD" : POP_2,
    "SHA256" : POP_1,
    "XOR_BLK": POP_2,
    "DUP_TOP": POP_1,
    "SWAP_TOP": POP_1,
}
