import unittest
import sys
import os

# Add memory object to path
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.dirname(  os.path.realpath( __file__ ) ) ), 'src', 'pipeline' ) )

from memory import Memory, Users, MemoryState

class TestMemory( unittest.TestCase ):
    def setUp( self ):
        self.mem =  Memory( 16, response_cycles=0, next_layer=Memory(
    128 // 4, response_cycles=3 ))

    def _test_internal_state( self, address, state,  user, access_counter_cache, access_counter_ram ):
        if self.mem.cache_on:
            # test cache values
            assert self.mem.access_stage == user
            assert self.mem.address == address
            assert self.mem.state == state
            assert self.mem.access_counter == access_counter_cache

        if access_counter_cache < 1:
            # test ram values
            assert self.mem.next_layer.access_stage == user
            assert self.mem.next_layer.address == address
            assert self.mem.next_layer.state == state
            assert self.mem.next_layer.access_counter == access_counter_ram

    
    def test_write( self ):
        val = 7
        val = val.to_bytes(4, 'big')
        address = 50
        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.write( address, val, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert MemoryState.IDLE == self.mem.write( address, val, Users.MEMORY )
        assert self.mem.next_layer.mem[ address // 4 ][ address % 4 ] == val
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )


    def test_read( self ):
        val = 58
        val = val.to_bytes(4, 'big')
        address = 98
        self.mem.next_layer.mem[ address // 4 ][ address % 4 ] = val

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )

    def test_cache_hit( self ):
        val = 58
        val = val.to_bytes(4, 'big')
        address = 23
        self.mem.next_layer.mem[ address // 4 ][ address % 4 ] = val

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )

    def test_cache_miss( self ):
        # first read value to get into cache
        val = 58
        val = val.to_bytes(4, 'big')
        address = 112
        self.mem.next_layer.mem[ address // 4 ][ address % 4 ] = val

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )
        
        # now rewrite new value
        val = 12
        val = val.to_bytes(4, 'big')

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.write( address, val, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert MemoryState.IDLE == self.mem.write( address, val, Users.MEMORY )
        assert self.mem.next_layer.mem[ address // 4 ][ address % 4 ] == val
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )

        # Read again, should result in miss
        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )

    def test_cache_reassignment( self ):
        # first read value to get into cache
        val = 12564
        val = val.to_bytes(4, 'big')
        address = 0
        self.mem.next_layer.mem[ address // 4 ][ address % 4 ] = val

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )
        
        # now read address that will override value in cache
        val = 3872342
        val = val.to_bytes(4, 'big')
        address = 64
        self.mem.next_layer.mem[ address // 4 ][ address % 4 ] = val

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )
    
        # Read address 0 again, should result in miss
        val = 12564
        val = val.to_bytes(4, 'big')
        address = 0

        for i in range( 2 ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )
    
    def test_muli_access( self ):
        val = 356
        val = val.to_bytes(4, 'big')
        address = 12

        assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
        self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 )

        # try reading different address
        address_new = 45
        for _ in range( 5 ):
            assert MemoryState.BUSY == self.mem.read( address_new, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 )

        # try reading same address different user
        address_new = 45
        for _ in range( 5 ):
            assert MemoryState.BUSY == self.mem.read( address_new, Users.FETCH )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 )
   
    def test_no_cache( self ):
        val = 58
        val = val.to_bytes(4, 'big')
        address = 65
        self.mem.set_cache( False )
        self.mem.next_layer.mem[ address // 4 ][ address % 4 ] = val

        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )
       
        # Read again, should result in miss
        for i in range( 2  ): 
            assert MemoryState.BUSY == self.mem.read( address, Users.MEMORY )
            self._test_internal_state( address, MemoryState.BUSY, Users.MEMORY, -1, 1 - i )
        assert val  == self.mem.read( address, Users.MEMORY )[ address % 4 ]
        self._test_internal_state( address, MemoryState.IDLE, Users.MEMORY, -1, 0 )

