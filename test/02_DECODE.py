import unittest
import sys
import os

try:
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))), 'src', 'pipeline'))
    from decode import *
except ImportError:
    print("Error: failed to import module")
    sys.exit(1)


class TestDecode(unittest.TestCase):
    def test_DECODE_NOOP(self):
        decode = Decode()
        curr_instr = decode.decode(Op.NOOP)
        expected_instr = {'Op': Op.NOOP, 'Operand_1': None, 'Operand_2': None,
                          'Operand_3': None, 'is_alu': False, 'is_branch': False, 'is_mem_access': False}
        self.assertEqual(curr_instr, expected_instr), "Decode test failed"

    def test_DECODE_STACK_PUSH_POP(self):
        decode = Decode()
        stack_size = registers.STACK.top_index
        registers.STACK.push(23)
        registers.STACK.push(47)
        self.assertEqual(registers.STACK.top_index,
                         stack_size + 2), "Stack push failed"
        stack_size = registers.STACK.top_index
        decode.decode(Op.ADD)
        self.assertEqual(registers.STACK.top_index,
                         stack_size - 2), "Stack pop failed"

    def test_DECODE_POP_2(self):
        decode = Decode()
        registers.STACK.push(1)
        registers.STACK.push(2)
        test_instr = decode.decode(Op.ADD)
        expected_instr = {'Op': Op.ADD, 'Operand_1': 2, 'Operand_2': 1,
                          'Operand_3': None, 'is_alu': True, 'is_branch': False, 'is_mem_access': False}
        self.assertEqual(
            test_instr, expected_instr), "Decode test for ADD failed"


if __name__ == '__main__':
    unittest.main()
