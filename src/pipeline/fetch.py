from memory import MemoryState, Users
from stage_state import StageState
import registers

class Fetch:
    # TODO: Add support for instruction offset
    
    def __init__(self):
        # setting initial values for the fetch stage
        self.status = StageState.IDLE
        self.address = 0
        self.offset = 0
        self.instr_buff = b'\x00'
        self.instr_buff_valid = False
        self.should_squash = False
        self.issued_instr = None
        self.reading = False
        self.instr_per_word = 4
        self.should_issue = True
    def load(self, address):
        # When the address is not in the cache it will return BUSY and stall the pipeline
        # else it will return the data and continue the pipeline

        # Set the fetch status to stall by default
        self.status = StageState.STALL

        # if offset is not zero ( and no squash ) then we have the current IR buffered
        if self.instr_buff_valid:
            return self.instr_buff
        return registers.MEMORY.read(address, Users.FETCH)

    def fetch(self, decode_state=StageState.STALL, should_issue=True):

        # check to see if fetch should do anything
        # if we shouldn't issue but we are currently in the prcoess of a read
        # finish read 
        if should_issue or self.reading:
           
            if not self.reading:
                # Get the PC and the instruction offset
                self.address = registers.PC
                self.offset = registers.INSTR_OFFSET
                self.reading = True
                # if gotten a signal while reading to squash 
                # while reading, invalidate buffer
                if self.should_squash:
                    self.instr_buff_valid = False
                self.should_squash = False

            load_data = self.load( self.address )
            # Check if the memory or the decode stage is busy
            if load_data != MemoryState.BUSY:
                self.reading = False
                # Set the fetch status to idle
                self.status = StageState.IDLE

                # Extract the instruction from the load data
                if isinstance( load_data, list ):
                    load_data = load_data[ self.address % 4 ]

                # set IR buffer
                self.instr_buff = load_data
                self.instr_buff_valid = True
                
                if decode_state != StageState.STALL and should_issue:
                
                    # Update the PC and the instruction offset, only if not getting squashed!
                    if not self.should_squash:
                        registers.INSTR_OFFSET = self.offset + 1
                        registers.PC = self.address + registers.INSTR_OFFSET // self.instr_per_word
                        registers.INSTR_OFFSET = registers.INSTR_OFFSET % self.instr_per_word
                    
                    # set IR valid
                    self.instr_buff_valid = registers.INSTR_OFFSET > 0
                    
                    load_data_pc_offset = load_data[ self.offset ]
                    # reset state and return instr object
                    self.issued_instr = { 'instr': load_data_pc_offset, 'squash' : self.should_squash }
                    return self.issued_instr

        # If the memory or the decode stage is busy, return Op.NOOP
        self.issued_instr = { 'instr': (46 + (2<<6)), 'squash': self.should_squash }
        self.should_issue = should_issue
        return self.issued_instr

    def fetch_back_pass(self, decode_status):
        if decode_status['status'] == StageState.STALL:
            self.status = StageState.STALL
        if decode_status.get( 'squash', False ):
            self.should_squash = True
            # invalidate IR buffer
            self.instr_buff_valid = False
        return decode_status

    def fetch_forward_pass(self, decode_status, should_issue):
        return self.fetch(decode_state=decode_status['status'], should_issue=should_issue) 
    def get_state( self ):
        return [
                'Status: {}'.format( self.status.name ),
                'Reading: {}'.format( 'Yes' if self.reading else 'No' ),
                'Instru Buffer: {} {}'.format( self.instr_buff.hex(), 'Valid' if self.instr_buff_valid  else 'Invalid' ), 
                'Will Squash: {}'.format( 'Yes' if self.should_squash  else 'No' ),
                'Issued Instr {}'.format( hex( self.issued_instr[ 'instr' ] )  if self.issued_instr else '' )
        ]
