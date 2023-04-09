import unittest
import sys
import os
import pprint
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


class TestExecute(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.execute_stage = ExecuteStage()
        self.instr = None

        def execute():
            self.execute_stage.execute_forward_pass(self.instr)
            return self.execute_stage.execute_back_pass()
        self.execute = execute
        self.decode = Decode().decode
        self.fetch = Fetch().fetch
        self.empty_stack = [0] * 32

    def test_EXECUTE_ALU_ADD(self):
        stack_size = registers.STACK.top_index

        self.instr = self.decode(int(b'00000011', 2))  # PUSH_VAL 3
        self.execute()

        self.instr = self.decode(int(b'00000111', 2))  # PUSH_VAL 7
        self.execute()

        self.assertEqual(registers.STACK.top_index,
                         stack_size + 2), "Stack size incorrect"
        expect_stack = self.empty_stack.copy()
        expect_stack[0] = 3
        expect_stack[1] = 7
        self.assertEqual(registers.STACK.stack,
                         expect_stack), "Stack push failed"

        self.instr = self.decode(16 + (2 << 6))  # ADD
        self.execute()
        expect_val = 10
        self.assertEqual(registers.STACK.remove(), expect_val), "Add failed"

    def test_EXECUTE_BRANCH_JMP_IF_1(self):
        expect_instr_offset = 2
        expect_pc = 31

        self.instr = self.decode(expect_instr_offset)  # PUSH_VAL 2
        self.execute()
        self.instr = self.decode(expect_pc)  # PUSH_VAL 31
        self.execute()

        self.instr = self.decode(12 + (2 << 6))  # JMP_IF_1
        self.execute()
        self.assertEqual(registers.PC, expect_pc), "JMP_IF_1 failed"
        self.assertEqual(registers.INSTR_OFFSET,
                         expect_instr_offset), "JMP_IF_1 failed"

    def test_EXECUTE_BRANCH_JMP_IF_0(self):
        expect_instr_offset = 3
        expect_pc = 17

        self.instr = self.decode(expect_instr_offset)  # PUSH_VAL 3
        self.execute()
        self.instr = self.decode(expect_pc)
        self.execute()

        self.instr = self.decode(13 + (2 << 6))  # JMP_IF_0
        self.execute()
        self.assertEqual(registers.PC, expect_pc), "JMP_IF_0 failed"
        self.assertEqual(registers.INSTR_OFFSET,
                         expect_instr_offset), "JMP_IF_0 failed"

    def test_EXECUTE_MEM_STR_32(self):
        store_val = 12
        except_val = b'\x00\x00\x00\x0c'
        address = 101

        self.instr = self.decode(store_val)  # PUSH_VAL 12
        self.execute()

        self.instr = {'Op': instructions.Op.POP,
                      'Operand_1': None, 'Operand_2': None, 'Operand_3': None}
        self.execute()

        self.instr = {'Op': instructions.Op.STR_32,
                      'Address': address, 'is_mem_access': True}

        while self.execute()['status'] == StageState.STALL:
            pass

        self.assertEqual(
            registers.MEMORY.next_layer.mem[address//4][address % 4], except_val), "STR_32 failed"


    def test_EXECUTE_MEM_LDR_32(self):
        except_val = b'\x00\x00\x00\x0c'
        address = 101

        self.test_EXECUTE_MEM_STR_32()

        self.instr = {'Op': instructions.Op.LDR_32,
                      'Address': address, 'is_mem_access': True}
        while self.execute()['status'] == StageState.STALL:
            pass
        self.assertEqual(registers.MEMORY.mem[9][address % 4], except_val), "LDR_32 failed"

if __name__ == '__main__':
    unittest.main()
