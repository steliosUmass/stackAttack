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
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.decode = Decode().decode

    def create_instruction(self, type=0, op=48, operand_1=None, operand_2=None, operand_3=None, is_alu=False, is_branch=False, is_mem_access=False, squash=False):
        return {
            'type': type,
            'Op': op,
            'Operand_1': operand_1,
            'Operand_2': operand_2,
            'Operand_3': operand_3,
            'is_alu': is_alu,
            'is_branch': is_branch,
            'is_mem_access': is_mem_access,
            'squash': squash
        }

    def test_DECODE_NOOP(self):
        curr_instr = self.decode(48)
        expected_instr = self.create_instruction(op=Op.NOOP)
        self.assertEqual(curr_instr, expected_instr), "Decode test failed"

    def test_DECODE_STACK_PUSH_POP(self):
        stack_size = registers.STACK.top_index
        registers.STACK.push(23)
        registers.STACK.push(47)
        self.assertEqual(registers.STACK.top_index,
                         stack_size + 2), "Stack push failed"
        stack_size = registers.STACK.top_index
        self.decode(16)
        self.assertEqual(registers.STACK.top_index,
                         stack_size - 2), "Stack pop failed"

    def test_DECODE_POP_2_ADD(self):
        registers.STACK.push(1)
        registers.STACK.push(2)
        test_instr = self.decode(16)
        expected_instr = self.create_instruction(
            op=Op.ADD, operand_1=2, operand_2=1, is_alu=True)
        self.assertEqual(
            test_instr, expected_instr), "Decode test for ADD failed"

    def test_DECODE_PUSH_VAL(self):
        # val is made up of 8 bits (left to right)
        # first bit is 1 - the type indicator,
        # next 2 bits are 00 - the op code for PUSH_VAL,
        # and the last 5 bits are 00011 - the operand
        curr_instr = self.decode(int(b'10000011', 2))
        expected_instr = self.create_instruction(
            type=1, op=Op.PUSH_VAL, operand_1=int(b'00011', 2))
        self.assertEqual(curr_instr, expected_instr), "Decode test failed"


if __name__ == '__main__':
    unittest.main()
