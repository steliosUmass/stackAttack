import sys

instr_mapping = {
    'PUSH_VAL': 0,
    'DUP': 2**6,
    'LDR_32': 2**7,
    'STR_32': 2**7 + 1,
    'PUSH': 2**7 + 6,
    'POP': 2**7 + 7,
    'JMP_IF_1': 2**7 + 9,
    'JMP_IF_0': 2**7 + 10,
    'ADD': 2**7 + 13,
    'EQ': 2**7 + 22,
    'NOOP': 2**7 + 45,
    'HALT': 2**7 + 46
}

program = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip('\n')
        if line == '' or line[0] == '#':
            continue
        line = line.split(' ')
        instr = line[0]
        operand = line[1] if len(line) > 1 else 0
        instr = instr_mapping[instr]
        operand = int(operand)
        line = instr + operand
        program.append(line)

b = bytearray()
file_to_write = sys.argv[2]

for instr in program:
    b.append(instr)
b = bytes(b)

with open(file_to_write, 'wb') as f:
    f.write(b)
