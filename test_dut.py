# Test DUT

import unittest
import logging
import sys

import bsdl_parser
from dut import DUT

# Allow to print DEBUG messages
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class DUTTestCase(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("DUT: ")
        self.parser = bsdl_parser.Parser('bsdl.ebnf')
        ast = self.parser.parseBSDL('bsdl/1k50f256.bsd')
        self.dev = DUT(ast)

    def test_IDCODE(self):
        id = self.dev.getID()
        print(id)
        self.assertEqual(id, "00010001000001010000000011011101")

    def test_register_parsing(self):
        self.dev.addRegisters()
        self.log.debug(self.dev.registers)
        self.log.debug(self.dev.instructions)
        self.assertEqual(len(self.dev.registers), 5)
        self.assertEqual(len(self.dev.instructions), 2)

    def test_instruction_parsing(self):
        self.dev.addRegisters()
        self.dev.addInstructions()
        self.log.debug(self.dev.registers)
        self.log.debug(self.dev.instructions)
        self.assertEqual(len(self.dev.instructions), 5)