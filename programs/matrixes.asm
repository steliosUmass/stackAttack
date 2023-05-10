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
.VAR MATRIX_3_LIMITER 2
# MATRIX_1_LIMITER + MATRIX_3_LIMITER + 2 (the last element is mainly accessed in the generator loop)
.VAR MATRIX_LIMITER_SUM 9

.VAR ADDR_ARRAY_1_LOCATION 40
.VAR ADDR_ARRAY_2_LOCATION 55
.VAR ADDR_ARRAY_3_LOCATION 65

# ADDR_ARRAY_3_LOCATION + MATRIX_3_SIZE (the algorithm increments before the check so we always overshoot by 1)
.VAR ADDR_ARRAY_3_END_LOCATION 71

.VAR ARRAY_3_LOC_STACK 31

# Bit 31 is the last. The alg can be modified to work on different sizes
HALT
# Bit 31 is the read location for array 1
# Bit 30 is the write location for array 3
PUSH_VAL ADDR_ARRAY_2_LOCATION
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
DUP
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

# UNTIL THIS POINT WE'VE LOADED THE FIST ARRAY

DUP MATRIX_LIMITER_SUM # DUP LAST ELEMENT ?
OUTER_LOOP_ARR_2: PUSH_VAL MATRIX_LIMITER_SUM
# [55 9]
PUSH_VAL 0
# mem counter [55 9 M]
PUSH_VAL 0
# stack counter [55 9 M S]
RESET_TO_ZERO: SWAP 2
# [55 S M 9]
POP
# why? [55 S M ]

# load the element from the mem counter + start location
INNER_LOOP_ARR_2: DUP
# [55 S M M_d]
DUP 3
# [55 S M M_d 55]
ADD
# [55 S M M_d+55]
# Generate the value and keep it in PUSH register until required
LDR_32
# [55 S M]
# Get the Matrix 3 value corresponding to the index we're at (stack counter + stack location)
DUP 1
# [55 S M S]
# Get the element of Matrix 1 corresponding to the index we're at
PUSH_VAL MATRIX_1_LIMITER
# [55 S M S 5]
PUSH_VAL 2
# [55 S M S 5 2]
ADD
# [55 S M S 7]
SWAP 1
# [55 S M 7 S]
SUB
# [55 S M 7-S]
DUP_TOP
# [55 S M 15]
# Push the value
PUSH
# [55 S M 15 10]
MUL
# [55 S M 150]
# Now we want to pull the M_3_i value
# Compute the write address
# [55 S M 150]
PUSH_VAL MATRIX_1_LIMITER
# [55 S M 150 5]
PUSH_VAL 3
# this is the offset for [.. S M 150 .. ]
# [55 S M 150 5 3]
PUSH_VAL MATRIX_3_LIMITER
# [55 S M 150 5 3 2] this is to compute the location of the M_3 in stack
ADD
# [55 S M 150 5 5]
ADD
# [55 S M 150 10]
DUP 2
# [55 S M 150 10 M]
SUB
# [55 S M 150 10-M]
SWAP 1
# [55 S M 10-M 150]
DUP 1
# [55 S M 10-M 150 10-M] 10-M+1 is where Matrix_3_M is as we have the product of values as a new term
PUSH_VAL 1
ADD
# [55 S M 10-M 150 10-M+1] 10-M+1 is where Matrix_3_M is
DUP_TOP
# [55 S M 10-M 150 0]
ADD
# [55 S M 10-M 150] MATRIX SUM WITH THE PREVIOUS ROW ELEMENT
SWAP 1
# [55 S M 150 10-M]
# Write the updated matrix value into the stack
SWAP_TOP
# [55 S M 0]
POP
# [55 S M]
PUSH_VAL 1
ADD
# [55 S M+1] # ready to access the next location
# NOW WE USE IT FOR LOOP CHECK
# Loop control
PUSH_VAL INNER_LOOP_ARR_2
# [55 S M+1 PC OFF]
DUP 2
# [55 S M+1 PC OFF M+1]
PUSH_VAL MATRIX_3_LIMITER
# [55 S M+1 PC OFF M+1 2]
EQ
# [55 S M+1 PC OFF 0]
JMP_IF_0
# [55 S M+1]
DUP 2
ADD
# [55 S M+MATRIX_3_LIMITER+55] gets us the second row from matrix 2
SWAP 2
POP
# [M+MATRIX_3_LIMITER+55 S]
PUSH_VAL 1
ADD
# [M+MATRIX_3_LIMITER+55 S+1] gets us the second column in the row for matrix 2
PUSH_VAL 0
# [M+MATRIX_3_LIMITER+55 0] gets us the second column in the row for matrix 2
PUSH_VAL INNER_LOOP_ARR_2
# [M+MATRIX_3_LIMITER+55 0 PC OFF]
DUP 4
# [M+MATRIX_3_LIMITER+55 0 PC OFF M+MATRIX_3_LIMITER]
PUSH_VAL ADDR_ARRAY_3_LOCATION
# [M+MATRIX_3_LIMITER+55 0 PC OFF M+1 65]
EQ
# [M+MATRIX_3_LIMITER+55 0 PC OFF 0]
JMP_IF_0

# Now we can POP out all the values until we hit the Matrix 3 ones
POP
POP
# [] removes M and S stack is now [ADDRs(3x) Matrix_3 Matrix_1_row]

PUSH_VAL 0
# [15 14 13 12 11 0]
POP_LOOP: SWAP 1
# [15 14 13 12 0 11]
POP
# [15 14 13 12 0]
PUSH_VAL 1
ADD
# [15 14 13 12 1]
PUSH_VAL POP_LOOP
# [15 14 13 12 1 PC OFF]
DUP 2
# [15 14 13 12 1 PC OFF 1]
PUSH_VAL MATRIX_1_LIMITER
# [15 14 13 12 1 PC OFF 1 5]
EQ
JMP_IF_0
# [15 5]
POP
# [15]
POP
# [] now the stack is just [Matrix_2_ADDR Matrix_1_ADDR Matrix_3_ADDR MATRIX_3_ROW]
# [55 45 65 410 345]

PUSH_VAL 0
# [55 45 65 410 345 WRITE_OFF]

WRITE_LOOP: SWAP 1
# [55 45 65 410 WRITE_OFF 345]
POP
# [55 45 65 410 WRITE_OFF]
PUSH_VAL MATRIX_3_LIMITER
# [55 45 65 410 WRITE_OFF 2]
DUP 1
# [55 45 65 410 WRITE_OFF 2 WRITE_OFF]
SUB
# [55 45 65 410 WRITE_OFF 2-WRITE_OFF] # is the location of the write base addr from the stack
DUP_TOP
# [55 45 65 410 WRITE_OFF 65]
DUP 1
ADD
# [55 45 65 410 WRITE_OFF 65+WRITE_OFF]
STR_32
# [55 45 65 410 WRITE_OFF]
PUSH_VAL 1
ADD
# [55 45 65 410 WRITE_OFF+1]
PUSH_VAL WRITE_LOOP
# [55 45 65 410 WRITE_OFF+1 PC OFF]
DUP 2
# [55 45 65 410 WRITE_OFF+1 PC OFF WRITE_OFF+1]
PUSH_VAL MATRIX_3_LIMITER
# [55 45 65 410 WRITE_OFF+1 PC OFF WRITE_OFF+1 2]
EQ
JMP_IF_0

POP
# [Matrix_2_ADDR Matrix_1_ADDR Matrix_3_ADDR]
PUSH_VAL MATRIX_3_LIMITER
ADD
# [Matrix_2_ADDR Matrix_1_ADDR NEW_Matrix_3_ADDR]
PUSH_VAL OUTER_LOOP_ARR_3
DUP 3
PUSH_VAL ADDR_ARRAY_2_LOCATION
EQ
HALT
HALT
JMP_IF_0
HALT

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