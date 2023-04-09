import unittest
import sys
import os

try:
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))), 'src', 'pipeline'))
    from fetch import *
    from decode import *
    from execute import *
    import registers
except ImportError:
    print("Error: failed to import module")
    sys.exit(1)


class TestIntegration(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.instr = None
        self.execute = ExecuteStage()
        self.decode = Decode()
        self.fetch = Fetch()
        self.empty_stack = [0] * 32
        self.new_instr = {
            'type': 1,
            'Op': Op.NOOP,
            'Operand_1': None,
            'Operand_2': None,
            'Operand_3': None,
            'Address': None,
            'Condition': None,
            'is_alu': False,
            'is_branch': False,
            'is_mem_access': False,
            'squash': False
        }
        registers.STACK.stack = self.empty_stack.copy()

    def test_FETCH_DECODE(self):
        write_val = 33796240  # PUSH_VAL 2, PUSH_VAL 3, NOOP, ADD
        for i in range(5):
            registers.MEMORY.write(
                registers.PC, int(write_val).to_bytes(4, 'big'), Users.FETCH)

        # print("\nExecuting \n\nPUSH_VAL 2\nPUSH_VAL 3\nADD")
        expect_output = ['[]', '[]', '[]', '[]',
                         '[]', '[]', '[2]', '[2, 3]', '[]', '[5]']

        for i in range(10):
            execute_status = self.execute.execute_back_pass()
            decode_status = self.decode.decode_back_pass(execute_status)
            self.fetch.fetch_back_pass(decode_status)
            todo_instr = self.fetch.fetch_forward_pass(decode_status, True)
            curr_instr = self.decode.decode_forward_pass(todo_instr)
            self.execute.execute_forward_pass(curr_instr)
            # print("\nPC", registers.PC, "OFFSET:", registers.INSTR_OFFSET)
            # print("INSTR:", curr_instr['Op'], curr_instr['Operand_1'])
            # print("STACK:", registers.STACK)
            self.assertEqual(registers.STACK.__str__(),
                             expect_output[i]), "Execute back pass failed"

if __name__ == '__main__':
    unittest.main()
