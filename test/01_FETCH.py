import unittest
import sys


try:
    sys.path.append('src/pipeline')
    from fetch import *
except ImportError:
    sys.path.append('../src/pipeline')
    from fetch import *


class TestFetch(unittest.TestCase):
    def test_FETCH_PASS(self):
        def write(clock, pc, write_val, decode=Decode()):
            for i in range(5):
                # print("clock: ", clock + i, "op:",
                #       decode.decode(48), "write val: ", write_val)
                registers.MEMORY.write(
                    pc, int(write_val).to_bytes(4, 'big'), Users.FETCH)
        clock = 0
        outputs = []
        expected_outputs = [48, 48, 48, 48, 10, 12, 25, 16]
        registers.PC = 2
        registers.INSTR_OFFSET = 0
        fetch = Fetch()
        decode = Decode()
        decode_status = StageState.STALL
        max_clock = 13
        write_val = 168565008
        while clock < max_clock:
            clock += 1
            if clock == 5:
                decode_status = StageState.IDLE
                write(clock, registers.PC, write_val, decode)
                clock += 5

            op = fetch.fetch(
                registers.PC, registers.INSTR_OFFSET, decode_status)
            # print("clock:", clock, "op:", decode.decode(op))
            outputs.append(decode.decode(op).value)
        self.assertEqual(outputs, expected_outputs), "Fetch test failed"


if __name__ == '__main__':
    unittest.main()
    
