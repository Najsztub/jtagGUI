import unittest
import logging
import sys
import random
import pprint

from HWLayer import bsdl_parser
from HWLayer.dut import DUT

# Allow to print DEBUG messages
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class DUTTestCaseEP4(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("DUT: ")
        self.parser = bsdl_parser.Parser('bsdl/bsdl.ebnf')
        ast = self.parser.parseBSDL('bsdl/EP4CE15F23.bsdl')
        self.dev = DUT(ast)

    def test_IDCODE(self):
        id = self.dev.getBSDL_IDCODE()
        print(id)
        self.assertEqual(id, "00000010000011110010000011011101")

    def test_register_parsing(self):
        self.dev.addRegisters()
        self.log.debug(self.dev.registers)
        self.log.debug(self.dev.instructions)
        self.assertEqual(len(self.dev.registers), 5)
        self.assertEqual(len(self.dev.instructions), 5)

    def test_instruction_parsing(self):
        self.dev.addRegisters()
        self.dev.addInstructions()
        self.log.debug(self.dev.registers)
        self.log.debug(self.dev.instructions)
        self.assertEqual(len(self.dev.instructions), 5)

    def test_bsr_adding(self):
        self.dev.addCells()
        self.assertEqual(len(self.dev.bsr_cells), 1080)
        self.assertIsNotNone(self.dev.bsr_cells[50])
        self.log.debug(self.dev.bsr_cells[50])

    def test_bsr_parsing(self):
        self.dev.addCells()
        bsr_len = [r[1] for r in self.dev.registers if r[0] == 'BSR'][0]
        self.assertEqual(bsr_len, len(self.dev.bsr_cells))
        s = random.randint(0, 2**bsr_len - 1)
        bsr = "{0:b}".format(s).zfill(bsr_len)

        # Set IOF15 to 1
        index = len(bsr) - 48 - 1
        bsr = bsr[:index] + '1' + bsr[index + 1:]
        self.dev.parseBSR(bsr)
        pin_st = self.dev.ports['IOF15'].pins[0].read
        self.assertEqual('1', pin_st)

        # Set IOF15 to 0
        bsr = bsr[:index] + '0' + bsr[index + 1:]
        self.dev.parseBSR(bsr)
        pin_st = self.dev.ports['IOF15'].pins[0].read
        self.assertEqual('0', pin_st)

        # Set IOF15 to 0 - by pin
        idx_end = len(bsr) - 48 - 1
        idx_start = len(bsr) - 50 - 1
        bsr = self.dev.setBSR()[1]
        self.log.debug('Cell+ctrl: '.format(bsr[idx_start:idx_end]))
        self.dev.ports['IOF15'].write = '0'
        bsr = self.dev.setBSR()[1]
        self.log.debug('Cell+ctrl: '.format(bsr[idx_start:idx_end]))
        self.assertEqual('00', bsr[idx_start:idx_end])

        # Set IOF15 to 1 - by pin
        self.dev.ports['IOF15'].write = '1'
        bsr = self.dev.setBSR()[1]
        self.log.debug('Cell+ctrl: '.format(bsr[idx_start:idx_end]))
        self.assertEqual('10', bsr[idx_start:idx_end])

    def test_real_bsr(self):
        self.dev.addCells()
        bsr = '010011010011011011010011010010011011011011010011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011011010110111111111110111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111010010011011011010011011011011011011011011011011010011011011011010011011011011011011011011011011011011011011011011011011011011011011011010010011011011011011011011011011010010011011010011011010011011011011011011011011011011011011011011011000111111111111111111111111111111111110111111111111110111111111111111111111111111110111111110110111111110111111111111110111111111110111111111111110111110111111111101000'
        self.dev.parseBSR(bsr)
        pp = pprint.PrettyPrinter(indent=2)
        self.log.debug(pp.pprint(self.dev.pins))