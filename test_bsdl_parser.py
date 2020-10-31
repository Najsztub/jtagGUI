import unittest
import bsdl_parser 

class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = bsdl_parser.Parser('bsdl.ebnf')

    def test_example_parsing(self):
        ast = self.parser.parseBSDL('bsdl/1k50f256.bsd')
        self.assertIsNotNone(ast)
        self.assertEqual(ast["component_name"],  "EP1K50F256")