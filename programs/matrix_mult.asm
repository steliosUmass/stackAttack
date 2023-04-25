# a b c d  * 1 2
# e f g h    3 4
#            5 6
#            7 8
#
#   a*1 a*2
# + b*3 b*4
# + c*5 c*6
# + d*7 d*8
#
# then do the same for e f g h

# so it's M_1(0,0) * M_2(0,0) and M_1(0,0) * M_2(0,1)

.VAR ADDR_MATRIX_DESC 40
.VAR ADDR_MATRIX_CTRS 44

.VAR MATRIX_1_SIZE 8
.VAR MATRIX_2_SIZE 8
.VAR MATRIX_3_SIZE 4

.VAR ADDR_MATRIX_1_size 44
.VAR ADDR_MATRIX_1_ROW_CTR 45
.VAR ADDR_MATRIX_2_size 46
.VAR ADDR_MATRIX_2_ROW_CTR 47
.VAR ADDR_MATRIX_3_size 48
.VAR ADDR_MATRIX_3_ROW_CTR 49

.VAR MATRIX_1_ROWS 2
.VAR MATRIX_1_COLS 4
.VAR MATRIX_2_ROWS 4
.VAR MATRIX_2_COLS 2
.VAR MATRIX_3_ROWS 2
.VAR MATRIX_3_COLS 2

.VAR ADDR_ARRAY_1_LOCATION 52
.VAR ADDR_ARRAY_2_LOCATION 60
.VAR ADDR_ARRAY_3_LOCATION 68

HALT

PUSH_VAL ADDR_ARRAY_1_LOCATION
PUSH_VAL MATRIX_1_SIZE
FETCH_MATRIX_1_ELE: DUP 1
LDR_32
PUSH
SWAP 2
PUSH_VAL 1
ADD
SWAP 1
PUSH_VAL 1
SUB
PUSH_VAL FETCH_MATRIX_1_ELE
DUP 2
PUSH_VAL 0
EQ
JMP_IF_0
POP
POP

HALT

PUSH_VAL ADDR_ARRAY_2_LOCATION
PUSH_VAL MATRIX_2_SIZE
FETCH_MATRIX_2_ELE: DUP 1
LDR_32
PUSH
SWAP 2
PUSH_VAL 1
ADD
SWAP 1
PUSH_VAL 1
SUB
PUSH_VAL FETCH_MATRIX_2_ELE
DUP 2
PUSH_VAL 0
EQ
JMP_IF_0
POP
POP

HALT

PUSH_VAL MATRIX_1_COLS
PUSH_VAL MATRIX_2_COLS

FINISH: HALT

# Row 1, Col 1, Row 2, Col 2
.ADDR ADDR_MATRIX_DESC
.LOAD 2 4 4 2

# Matrix 1 size, Row size, Matrix 2 size, Row size, Matrix 3 size, Row size
.ADDR ADDR_MATRIX_CTRS
.LOAD 8 4 8 2
.LOAD 4 2 0 0

.ADDR ADDR_ARRAY_1_LOCATION
.LOAD 8 7 6 5
.LOAD 4 3 2 1

.ADDR ADDR_ARRAY_2_LOCATION
.LOAD 101 102
.LOAD 103 104
.LOAD 105 106
.LOAD 107 108

.ADDR ADDR_ARRAY_3_LOCATION
.LOAD 0 0 0 0