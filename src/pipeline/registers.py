from memory import Memory


class Stack():
    """
    Used to model array of registers for stack machine
    size:
        size of stack
    """

    def __init__(self, size):
        self.stack = []
        # -1 means that stack is empty
        self.top_index = -1
        for _ in range(size):
            self.stack.append(0)

    def push(self, val):
        '''pushes the value from the push register to the stack'''

        # if there is no overflow
        if self.top_index < len(self.stack) - 1:
            self.top_index += 1
            self.stack[self.top_index] = val
        else:
            # need to shift everything down, the oldest value is lost
            for i in range(len(self.stack) - 1):
                self.stack[i] = self.stack[i + 1]
            self.stack[self.top_index] = val

    def pop(self):
        global POP
        '''pops value from top of stack into POP register'''
        val = self.remove( )
        if val is not None:
            POP = val
    
    def remove(self):
        global POP
        '''pops value from top of stack and returns it'''
        val = None
        # if stack is empty, do nothing
        if self.top_index > -1:
            val = self.stack[self.top_index]
            self.top_index -= 1
        return val


    def __str__(self):
        if self.top_index > -1:
            return str(self.stack[:self.top_index + 1])
        else:
            return '[]'


# singletons
PC = 0
POP = 0
PUSH = 0
LINK = 0
INSTR_OFFSET = 0
STACK = Stack(32)
MEMORY = Memory(16, response_cycles=0, next_layer=Memory(
    32000 // 4, response_cycles=3))

# if __name__ == '__main__':
#     # set push reg to 156
#     SpecialRegisters.PUSH = 156
#     SpecialRegisters.STACK.push()
#     SpecialRegisters.PUSH = 12
#     SpecialRegisters.STACK.push()
#     SpecialRegisters.PUSH = 130
#     for i in range(30):
#         SpecialRegisters.STACK.push()

# #    print( SpecialRegisters.STACK.stack )
#     SpecialRegisters.PUSH = 98
#     SpecialRegisters.STACK.push()
# #    print( SpecialRegisters.STACK.stack )
#     SpecialRegisters.STACK.pop()
#     print(SpecialRegisters.POP)
#     SpecialRegisters.PUSH = 23
#     SpecialRegisters.STACK.push()
#     print(SpecialRegisters.STACK.stack)
