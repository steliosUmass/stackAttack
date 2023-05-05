.VAR BOB_PUB_KEY_LOC 100
.VAR AES_LOC 200
.VAR MESSAGE_LOC 300
.VAR MESSAGE_LENGTH 12

# group is mod 97
PUSH_VAL 97

# generate private key
RAND_INT

# get BOBs public key
PUSH_VAL BOB_PUB_KEY_LOC
LDR_64
PUSH

# generate key
DH
DUP 0

# push message length
PUSH_VAL MESSAGE_LENGTH

# push message location
PUSH_VAL MESSAGE_LOC

# call encryption function
PUSH_VAL AES_CBC_ENC
SR
HALT

# now decrypt
# push message length
PUSH_VAL MESSAGE_LENGTH

# push message location
PUSH_VAL MESSAGE_LOC

# call encryption function
PUSH_VAL AES_CBC_DEC
SR
HALT

.ADDR BOB_PUB_KEY_LOC 
.LOAD 45 34578

.ADDR MESSAGE_LOC  
.LOAD 0x48656c6c 0x6f20576f 0x726c6421 0x2057656c 0x636f6d65 0x20746f20 0x6f757220 0x776f6e64 0x65726675 0x6c204465 0x6d6f2120 0x54686973 0x2064656d 0x6f207769 0x6c6c2073 0x686f7720 0x796f7520 0x686f7720 0x41455320 0x43424320 0x776f726b 0x732e2048 0x6f706566 0x756c6c79 0x2c207768 0x656e2049 0x20656e63 0x72797074 0x20746869 0x73206d65 0x73736167 0x6520616e 0x64206465 0x63727970 0x74206974 0x20726574 0x75726e73 0x20626163 0x6b20746f 0x206e6f72 0x6d616c2e 0x20497420 0x77696c6c 0x20626520 0x76657279 0x20656d62 0x61727261 0x7373696e 0x67206966 0x20697420 0x646f6573 0x6e27742e

.ADDR AES_LOC
FUNC AES_CBC_ENC
# i val
PUSH_VAL 0

# generate IV
RAND_BLK

# read current block
LOOP_ENC: DUP 1
DUP 3
ADD
DUP 0
LDR_128
PUSH

# write previous block to same location
SWAP 1
DUP 2
POP
STR_128

# xor to get value to give to AES
XOR_BLK

# get key to top and put it in right place
DUP 4
SWAP 1

# call aes
AESE

# increment i
SWAP 1
PUSH_VAL 1
ADD
SWAP 1

# check to see if i is equal to message block length
PUSH_VAL LOOP_ENC
DUP 3
DUP 6
EQ
JMP_IF_0

# now we need to save the final block
POP
ADD 
STR_128

# pop length and key
POP
POP

RET

FUNC AES_CBC_DEC
# get IV 
DUP 1
LDR_128
PUSH

# i val
PUSH_VAL 1

# get block at i location and push two copies
LOOP_DEC: DUP 0
DUP 3
ADD
LDR_128
PUSH
PUSH

# decrypt block
DUP 6
SWAP 1
AESD

# xor to get plain text
SWAP 1
SWAP 3
XOR_BLK

# save block to current i - 1
POP
DUP 0
PUSH_VAL 1
SUB
DUP 3
ADD
STR_128

# incerment i and see if it is equal to message length + 1
PUSH_VAL LOOP_DEC
DUP 2
DUP 6
PUSH_VAL 1
ADD
EQ
JMP_IF_0

# pop i, last cipher block, message loc, length, and key
POP
POP
POP
POP
POP
RET
