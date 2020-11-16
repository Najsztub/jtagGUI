# Mock UrJTAG module for GUI development without UrJTAG bindings
# Examlpe 1 part chain with 1k59f256.bsd

import sys
import random

class chain:
  def __init__(self):
    self.cur_inst = None
    self.bsr_len = None
    self.regs = {'BYPASS': 1}
    self.instructions = {}

  def cable(self, *args):
    self.j_cable = args[0]

  def tap_detect(self):
    sys.stdout.write("Detected chain of 5")

  def len(self):
    return 5

  def part(self, id):
    if id == 0 : self.bsr_len = 798
    elif id == 1: self.bsr_len = 100
    elif id == 2: self.bsr_len = 240
    elif id == 3: self.bsr_len = 960
    elif id == 4: self.bsr_len = 202
    else: pass

  def addpart(self, ir_len):
    self.part(0)
  
  def partid(self, id):
    if id == 0: return int('00010001000001010000000011011101', 2)
    elif id == 1: return int('11010001011001010000000011011101', 2)
    elif id == 2: return int('00000010000010100001000011011101', 2)
    elif id == 3: return int('00000001000001010000000011011101', 2)
    elif id == 4: return int('00101000001001110000000000010011', 2)

    else: return None
    
  def set_trst(self, st):
    pass

  def reset(self):
    pass

  def set_instruction(self, instr):
    self.cur_inst = instr

  def shift_ir(self):
    pass

  def shift_dr(self):
    pass

  def get_dr_in(self):
    s = random.randint(0, 2**self.bsr_len - 1)
    return s

  def get_dr_out(self):
    return self.get_dr_in()

  def get_dr_in_string(self):
    s = self.get_dr_in()
    return "{0:b}".format(s).zfill(self.bsr_len)

  def get_dr_out_string(self):
    return self.get_dr_in_string()

  def set_dr_in(self, val, start=None, end=None):
    pass

  def set_dr_out(self, val, start=None, end=None):
    self.set_dr_in(val, start, end)

  def add_register(self, reg, length):  # another register, with its  length
    self.regs[reg] = length

  def add_instruction(self, instr, opcode, reg):
    self.instructions[instr] = {'opcode' : opcode, 'reg' : reg}

if __name__ == "__main__":
  # Test mock
  urc = chain()
  urc.cable("JTAGKey")
  urc.reset()

  urc.addpart(8) # instruction length of the one chip on your chain.

  urc.add_instruction("CLAMP", "11101110", "BYPASS") # another instruction that selects the BYPASS register.  The bypass register always exists.

  urc.add_register("IDREG", 32);  # another register, with its  length
  urc.add_instruction("IDCODE", "11111110", "IDREG")  #

  # Then you can set and scan the new registers:

  urc.set_instruction("IDCODE")
  urc.shift_ir()
  urc.shift_dr()
  print(urc.get_dr_out_string())
