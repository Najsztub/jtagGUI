# BSDL parser class based on TaTsu
import tatsu

class BsdlSemantics:
  def __init__(self, model):
    self.bsdl_model = model

  def map_string(self, ast):
    ast = self.bsdl_model.parse(''.join(ast), "port_map")
    return ast

  def grouped_port_identification(self, ast):
    ast = self.bsdl_model.parse(''.join(ast), "group_table")
    return ast

class Parser:
  def __init__(self, ebnf_file):

    self.ebnf_file = ebnf_file
    self.grammar = open(ebnf_file).read()
    self.initialized = False

  def initialize(self):
    # tatsu.to_python_sourcecode(grammar)
    self.bsdl_model = tatsu.compile(self.grammar, ignorecase=True)
    self.initialized = True

  def parseBSDL(self, bsdl_file):
    if not self.initialized:
      self.initialize()
    bsdl_def = open(bsdl_file).read()
    return self.bsdl_model.parse(bsdl_def, "bsdl_description", semantics=BsdlSemantics(self.bsdl_model), parseinfo=False, ignorecase=True)

