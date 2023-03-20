from enum import Enum
cycles = 0

class MemoryState( Enum ):
    READING = 1
    WRITING = 2
    IDLE = 3 
    BUSY = 4 
class Users( Enum ): 
    USER1 = 1

class Memory():
    def __init__( 
            self, 
            num_words, 
            line_length=4, 
            word_length=4,
            reponse_cycles=1,
            next_layer=None 
        ):
        
        self.mem = []
        self.access_cycle = None 
        self.access_stage = None
        self.response_cycles = reponse_cycles        
        self.state = MemoryState.IDLE
        self.next_layer = next_layer
        
        # init memory to all 0
        for _ in range( num_words ):
            line = []
            for _ in range( line_length ):
                line.append( b'x\00' * word_length )
            self.mem.append( line )

    def read( self, index, user ):
        if self.state == MemoryState.IDLE:
            self.access_cycle = cycles
            self.access_stage = user
            self.state = MemoryState.READING
            return self.state

        elif Users.USER1 == self.access_stage and self.state == MemoryState.READING:
            if cycles >= self.response_cycles + self.access_cycle:
                # if the next layer is not none, than this is cache
                # check to see if we have it
                if self.next_layer is not None:
                   pass  

                else:
                    # else we are in ram, so get the value
                    self.state = MemoryState.IDLE
                    return self.mem[ index // 4 ][ index % 4 ]
            else:
                return self.state
        else:
            # the memory is busy
            return MemoryState.BUSY
        
        
    def write( self, index, value, user ):
        if self.state == MemoryState.IDLE:
            self.access_cycle = cycles
            self.access_stage = user
            self.state = MemoryState.WRITING
            return MemoryState.WRITING

        elif Users.USER1 == self.access_stage and self.state == MemoryState.WRITING:
            if cycles >= self.response_cycles + self.access_cycle:
                # if the next layer is not none, than this is cache
                # we want to write to ram so call write to next layer
                if self.next_layer is not None:
                    self.next_layer.write( index, value, user )
                else:
                    # else we are in ram, so get the value
                    self.mem[ index // 4 ][ index % 4 ] = value
                    self.state = MemoryState.IDLE
                    return self.state
            else:
                return self.state
        else:
            return MemoryState.BUSY

if __name__ == '__main__':

    m = Memory( 1000, reponse_cycles=5 )
    current_action = None
    while True:
        action = input()
        action = action.split()
        read_val = None
        write_val = None
        if len( action ) > 0 and current_action is None:
            current_action = action

        if current_action is not None:    
            if current_action[ 0 ] == 'READ':
                read_val = m.read( int( current_action[ 1 ] ),  Users.USER1 )
                
            elif current_action[ 0 ] == 'WRITE':
                write_val = m.write( int( current_action[ 1 ] ) , int( current_action[ 2 ] ).to_bytes( 4, 'big' ), Users.USER1 )

        print('-'*20 + 'Cycle {}'.format( cycles ) + '-'*20 )
       
        if current_action and current_action[ 0 ] == 'READ':
            print('READ val {}'.format( read_val ) )
            
            if read_val != MemoryState.READING:
                current_action = None

        elif current_action:
            print('WRITE val {}'.format( write_val ) )
            if write_val != MemoryState.WRITING:
                current_action = None
        
        cycles += 1 
