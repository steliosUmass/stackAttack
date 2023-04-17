.VAR ARRAY_LENGTH 3
.VAR ARRAY_LOCATION 100

# push index i inital value
PUSH_VAL 0

# push index j inital value
OUTER_LOOP: DUP 0
PUSH_VAL 1
ADD

# GET VALUE at ARRAY[ i ]
DUP 1
PUSH_VAL ARRAY_LOCATION
ADD
LDR_32
PUSH

# first check if j is equal to i
INNER_LOOP: PUSH_VAL FINISHED
DUP 3
PUSH_VAL ARRAY_LENGTH
EQ
JMP_IF_1

# GET VALUE at ARRAY[ j ]
DUP 1
PUSH_VAL ARRAY_LOCATION
ADD
LDR_32
PUSH

# PUSH VALUE TO BRANCH TOO
PUSH_VAL EXCHANGE

# COPY ARRAY[ i] and ARRAY[ j ] FOR CMP
DUP 3
DUP 3

# DO CMP and branch
LT
JMP_IF_1

# No exchanged need, pop ARRAY[ j ] and JMP to end of loop
POP
PUSH_VAL END_INNER
JMP

# SWAP ARRAY[ i ] and ARRAY[ j ]
EXCHANGE: SWAP 1
# POP ARRAY[ i ] and store it at ARRAY[ j ]
POP
DUP 1
PUSH_VAL ARRAY_LOCATION
ADD
STR_32

# POP copy of ARRAY[ j ] and store at ARRAY[ i ]
DUP 0
POP
DUP 2
PUSH_VAL ARRAY_LOCATION
ADD
STR_32

# increment j here and see if we should loop again
END_INNER: SWAP 1
PUSH_VAL 1
ADD
SWAP 1
PUSH_VAL INNER_LOOP
DUP 3
PUSH_VAL ARRAY_LENGTH
EQ
JMP_IF_0

# POP off ARRAY[ i ] and j
POP
POP

# increment i here and see if we should loop again
PUSH_VAL 1
ADD
PUSH_VAL OUTER_LOOP
DUP 2
PUSH_VAL ARRAY_LENGTH
EQ
JMP_IF_0

# finally halt
FINISHED: HALT

# PUT array in memory at location 100
.ADDR ARRAY_LOCATION

.LOAD 5 4 3
