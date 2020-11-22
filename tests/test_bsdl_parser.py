import unittest
import logging
import pprint
import sys

from HWLayer import bsdl_parser 

# Allow to print DEBUG messages
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = bsdl_parser.Parser('bsdl/bsdl.ebnf')
        self.log = logging.getLogger("Parser: ")

    def test_example_parsing(self):
        ast = self.parser.parseBSDL('bsdl/1k50f256.bsd')
        self.assertIsNotNone(ast)
        self.assertEqual(ast["component_name"],  "EP1K50F256")

    def test_Verde(self):
        ast = self.parser.parseBSDL('bsdl/Verde_Processor.bsdl')
        bsr = ast["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_register"]
        pp = pprint.PrettyPrinter(indent=2)
        self.log.debug(pp.pprint(bsr[15]))
        cell15_name = bsr[15]['cell_info']['cell_spec']['port_id']
        self.assertEqual(''.join(cell15_name), "NC(1)")