from enum import Enum

class MemoryState( Enum ):
    IDLE = 1 
    BUSY = 2 

class Users( Enum ): 
    USER1 = 1

class Memory():
    """
    Used to simulate cache or RAM
    
    num_lines : int
        number of lines this memory holds
    line_length : int
        length of each line in words 
    word_length : int
        length of each word in bytes
    response_cycles : int
        number of cycles it takes for this memory to respond to read/write
    next_layer : Memory
        a reference to the next level of memory in the hierachy. 
        If this is None, then its assumed memory is RAM
    """
    def __init__( 
            self, 
            num_lines, 
            line_length=4, 
            word_length=4,
            reponse_cycles=1,
            next_layer=None 
        ):
        
        self.mem = []

        # info used during access 
        self.access_counter = 0
        self.access_stage = None
        self.access_address = None
        self.response_cycles = reponse_cycles       
        self.state = MemoryState.IDLE
        self.next_layer = next_layer
        self.line_length = line_length
        
        # init memory to all 0
        for _ in range( num_lines ):
            line = []
            for _ in range( line_length ):
                line.append( b'x\00' * word_length )
            self.mem.append( line )

        # if this is true
        # we are cache, create valid array and tag array
        if next_layer is not None:
            self.valid =  [ False ] * num_lines 
            self.tag = [ 0 ] * num_lines 
        
            # if we are cache, get total memory space from next layer
            self.total_mem_space = next_layer.total_mem_space
        
        # for ram, use its current size
        else:
            self.total_mem_space = line_length * num_lines


    def _calc_index_and_tag( self, address ):
        '''
        Internal method used to compute tag and index integer values for cache
        '''
        index_mask_shift = ( self.line_length - 1 ).bit_length()
        memory_bit_length = ( len( self.mem ) - 1 ).bit_length() 
        index_mask = 2**memory_bit_length - 1 << index_mask_shift
        index = address & index_mask 
        
        # shift result back
        index = index >> index_mask_shift

        # calc tag

        # this value is bit 1 where index and offset are supposed to be 
        index_offset_mask = 2**index_mask_shift - 1 + index_mask

        # this value is bit 1 where tag is, and 0 where index and offset are
        tag_mask = ( 2**16 ) - 1 ^ index_offset_mask
        tag = address & tag_mask

        # shift result
        tag = tag >> index_offset_mask.bit_length()

        return tag, index

    def read( self, address, stage ):
        '''
        Reads a line that includes the addressed word
        
        Parameters
        ----------
        address : int
            2 byte address of word to be read. passed in as integer
        stage : Users
            stage of pipline which is accessing the memory

        Returns
        --------
        list or MemoryState
            Returns MemoryState.busy during read execution and list of bytes when finished

        Exceptions
        ----------
        NotImplementedError
            raised if address is larger than amount of words
        '''

        if self.state == MemoryState.IDLE:
            if address > self.total_mem_space:
                raise NotImplementedError
            self.access_counter = self.response_cycles - 1
            self.access_stage = stage
            self.address = address
            self.state = MemoryState.BUSY

        if stage == self.access_stage and  address == self.address:
            if self.access_counter < 1:
                # if the next layer is not none, than this is cache
                # check to see if we have it
                if self.next_layer is not None:
                    tag, index = self._calc_index_and_tag( address )

                    # check if hit
                    if self.valid[ index ] and self.tag[ index ] == tag:
                        # hit
                        self.state = MemoryState.IDLE
                        return self.mem[ index ]
                    
                    # else miss
                    val = self.next_layer.read( address, self.access_stage )
                    
                    # update cache
                    if val != MemoryState.BUSY:
                        self.valid[ index ] = True
                        self.tag[ index ] = tag
                        self.mem[ index ] = val
                    
                    self.state = MemoryState.IDLE
                    return val

                else:
                    # else we are in ram, so get the value
                    self.state = MemoryState.IDLE
                    return self.mem[ address // self.line_length ]
            else:
                self.access_counter -= 1
        return self.state
        
        
    def write( self, address, value, stage ):
        '''
        write a word that at specified address
        
        Parameters
        ----------
        address : bytes
            2 byte address of word to be written to. passed in as integer

        value : bytes
            4 byte value to be stored in memory
        stage : Users
            stage of pipline which is accessing the memory

        Returns
        --------
        MemoryState
            Returns MemoryState.busy during read execution and MemoryState.idle when write is complete
        Exceptions
        ----------
        NotImplementedError
            raised if address is larger than amount of words

        '''

        if self.state == MemoryState.IDLE:
            if address > self.total_mem_space:
                raise NotImplementedError
            # sub 1 in order for correct cycles 
            self.access_counter = self.response_cycles - 1
            self.access_stage = stage
            self.address = address
            self.state = MemoryState.BUSY

        if stage == self.access_stage and address == self.address:
            if self.access_counter < 1:
                # if the next layer is not none, than this is cache
                # we want to write to ram so call write to next layer
                
                if self.next_layer is not None:
                    # first invalid cache if it exists
                    _, index = self._calc_index_and_tag( address )
                    self.valid[ index ] = False 
                    status = self.next_layer.write( address, value, stage )
                    if status == MemoryState.IDLE:
                        self.state = MemoryState.IDLE
                    return status
                
                else:
                    # else we are in ram, so get the value
                    self.mem[ address // 4 ][ address % 4 ] = value
                    self.state = MemoryState.IDLE
                    return self.state
            else:
                self.access_counter -= 1
        
        return self.state

if __name__ == '__main__':
    
    from tabulate import tabulate
    cycles = 1
    m = Memory( 1000, reponse_cycles=3 )
    c = Memory( 16, reponse_cycles=0, next_layer=m )

    current_action = None
    while True:
        action = input()
        action = action.split()
        read_val = None
        write_val = None
       
        # implement view command 
        if len( action ) > 0 and action[ 0 ] == 'VIEW':
            memory = action[ 1 ]
            mem_index = int( action[ 2 ] ) // 4
            
            if memory == 'CACHE':
                row = [ mem_index, bin( c.tag[ mem_index ] ), c.mem[ mem_index ] , '1' if c.valid[ mem_index ] else '0' ]
                table = [ [ 'INDEX', 'TAG', 'INDEX', 'VALID' ], row ]

            elif memory == 'RAM':
                row = [ mem_index, m.mem[ mem_index ] ]
                table = [ [ 'INDEX', 'VALUE' ], row ]

            print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))

	# else continue simulation
        else:
            if len( action ) > 0 and current_action is None:
                current_action = action

            if current_action is not None:    
                if current_action[ 0 ] == 'READ':
                    read_val = c.read( int( current_action[ 1 ] ),  Users.USER1 )
                    
                elif current_action[ 0 ] == 'WRITE':
                    write_val = c.write( int( current_action[ 1 ] ) , int( current_action[ 2 ] ).to_bytes( 4, 'big' ), Users.USER1 )

            print('-'*20 + 'Cycle {}'.format( cycles ) + '-'*20 )
       
            if current_action and current_action[ 0 ] == 'READ':
                print('READ val {}'.format( read_val ) )
                
                if read_val != MemoryState.BUSY:
                    current_action = None

            elif current_action:
                print('WRITE val {}'.format( write_val ) )
                if write_val != MemoryState.BUSY:
                    current_action = None
            
            cycles += 1 
