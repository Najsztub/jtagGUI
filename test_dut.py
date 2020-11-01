# Test DUT

import unittest

import bsdl_parser
from dut import DUT

class DUTTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = bsdl_parser.Parser('bsdl.ebnf')
        ast = self.parser.parseBSDL('bsdl/1k50f256.bsd')
        self.dev = DUT(ast)

    def test_IDCODE(self):
        id = self.dev.getID()
        print(id)
        self.assertEqual(id, "00010001000001010000000011011101")