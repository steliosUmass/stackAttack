class Stack( ):
    """
    Used to model array of registers for stack machine
    size:
        size of stack
    """

    def __init__( self, size ):
        self.stack = []
        # -1 means that stack is empty
        self.top_index = -1
        for _ in range( size ):
            self.stack.append( 0 )

    def push( self ):
        '''pushes the value from the push register to the stack'''

        # if there is no overflow
        if self.top_index < len( self.stack ) - 1:
            self.top_index += 1
            self.stack[ self.top_index ] = SpecialRegisters.PUSH
        else:
            # need to shift everthing down, the oldest value is lost
            for i in range( len( self.stack ) - 1 ):
                self.stack[ i ] = self.stack[ i + 1 ]
            self.stack[ self.top_index ] = SpecialRegisters.PUSH
    
    def pop( self ):
        '''pops value from top of stack into POP register'''
        # if stack is empty, do nothing
        if self.top_index > -1:
            SpecialRegisters.POP = self.stack[ self.top_index ]
            self.top_index -= 1

class SpecialRegisters( ):
    PC = 0
    POP = 0
    PUSH = 0
    LINK = 0
    STACK = Stack( 32 )


if __name__ == '__main__':
    # set push reg to 156
    SpecialRegisters.PUSH = 156
    SpecialRegisters.STACK.push()
    SpecialRegisters.PUSH = 12
    SpecialRegisters.STACK.push()
    SpecialRegisters.PUSH = 130
    for i in range( 30 ):
        SpecialRegisters.STACK.push()
 
#    print( SpecialRegisters.STACK.stack )
    SpecialRegisters.PUSH = 98
    SpecialRegisters.STACK.push()
#    print( SpecialRegisters.STACK.stack )
    SpecialRegisters.STACK.pop()
    print(SpecialRegisters.POP )
    SpecialRegisters.PUSH = 23
    SpecialRegisters.STACK.push()
    print( SpecialRegisters.STACK.stack )
