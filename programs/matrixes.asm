# 5x3
# 2x5
# 3x2

.VAR MATRIX_1_SIZE 15
.VAR MATRIX_2_SIZE 10
.VAR MATRIX_3_SIZE 6

# The stack looks like this 
# Last 2 - Address locations for Matrix 1 and 3
# MATRIX_3_LIMITER number of Matrix 3 elements
# MATRIX_1_LIMITER number of Matrix 3 elements
# MATRIX_3_LIMITER number of Matrix 3 elements


# THE MAX SIZE OF THE NEXT 2 TOGETHER IS 24 (4 words x 6)
# other bits are
# 1 bit for limiter count of MATRIX 1
# 1 bit for limiter count of MATRIX 3
# 2 bits for operations (also for loop variables)
# 1 bit for EQ check

.VAR MATRIX_1_LIMITER 5
.VAR MATRIX_3_LIMITER 3
# MATRIX_1_LIMITER + MATRIX_3_LIMITER + 2 (the last 2 elements)
.VAR MATRIX_LIMITER_SUM 10

.VAR ADDR_ARRAY_1_LOCATION 40
.VAR ADDR_ARRAY_2_LOCATION 55
.VAR ADDR_ARRAY_3_LOCATION 65

.VAR ARRAY_3_LOC_STACK 31

# Bit 31 is the last. The alg can be modified to work on different sizes

# Bit 31 is the read location for array 1
# Bit 30 is the write location for array 3
PUSH_VAL ADDR_ARRAY_1_LOCATION
PUSH_VAL ADDR_ARRAY_3_LOCATION

# Pushes in [MATRIX_3_LIMITER x 0s] that is used to compute the indices of the 3rd matrix
OUTER_LOOP_ARR_3: PUSH_VAL MATRIX_3_LIMITER
INNER_LOOP_ARR_3: PUSH_VAL 0
SWAP 1
PUSH_VAL 1
SUB
PUSH_VAL INNER_LOOP_ARR_3
DUP 2
PUSH_VAL 0
EQ
JMP_IF_0

POP


OUTER_LOOP_ARR_1: PUSH_VAL MATRIX_3_LIMITER
PUSH_VAL 2
ADD
DUP 0
SWAP_TOP

# Pushes in MATRIX_1_LIMITER number of elements from MATRIX_1
PUSH_VAL MATRIX_1_LIMITER
INNER_LOOP_ARR_1: DUP 1
LDR_32
PUSH
SWAP 2
PUSH_VAL 1
ADD
SWAP 1
PUSH_VAL 1
SUB
PUSH_VAL INNER_LOOP_ARR_1
DUP 2
PUSH_VAL 0
EQ
JMP_IF_0

POP
PUSH_VAL MATRIX_LIMITER_SUM
SWAP_TOP
POP

PUSH_VAL MATRIX_LIMITER_SUM
PUSH_VAL 0
PUSH_VAL 0

INNER_LOOP_ARR_2: PUSH_VAL ADDR_ARRAY_2_LOCATION
# Generate the value and keep it in PUSH register until required
ADD
LDR_32

# Get the Matrix 3 value corresponding to the index we're at
SWAP 1
DUP
DUP 2
SUB
PUSH_VAL 1
SUB
DUP_TOP

# Get the element of Matrix 1 corresponding to the index we're at
PUSH_VAL MATRIX_1_LIMITER
PUSH_VAL 2
ADD
DUP 3
SUB
DUP_TOP

# Push the value
PUSH
MUL
ADD

# Compute the write address
DUP 1
DUP 3
SUB

# Write the updated matrix value into the stack
SWAP_TOP
POP
SWAP 1
PUSH_VAL 1
ADD
DUP

# Loop control
PUSH_VAL INNER_LOOP_ARR_2
DUP 2
PUSH_VAL MATRIX_3_LIMITER
EQ
JMP_IF_0


POP
POP
POP

PUSH_VAL MATRIX_1_LIMITER
POP_MATRIX_1_LOOP: SWAP 1
POP
PUSH_VAL 1
SUB
PUSH_VAL POP_MATRIX_1_LOOP
DUP 2
PUSH_VAL 0
EQ
JMP_IF_0
POP

FINISHED: HALT


.ADDR ADDR_ARRAY_1_LOCATION
.LOAD 15 14 13 12 11
.LOAD 20 19 18 17 16
.LOAD 25 24 23 22 21


.ADDR ADDR_ARRAY_2_LOCATION
.LOAD 10 9
.LOAD 8 7
.LOAD 6 5
.LOAD 4 3
.LOAD 2 1

.ADDR ADDR_ARRAY_3_LOCATION
.LOAD 0 0 0
.LOAD 0 0 0