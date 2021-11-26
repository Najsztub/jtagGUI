import sys

if len(sys.argv) > 1 and sys.argv[1] == "DEBUG":
  from HWLayer import urjtag_mock as urjtag
else:
  import urjtag

# For showing stdout from UrJTAG in log
# https://stackoverflow.com/questions/5136611/capture-stdout-from-a-script
from contextlib import redirect_stdout
from io import StringIO

#######################################################################
# Override UrJTAG class to include DUT processing
class JTAG(urjtag.chain):
  def __init__(self):
    #initialize parent class
    urjtag.chain.__init__(self)
    self.devs = []
    self.active_dev = None
  
  def addDevs(self, dev_list):
    for dev in dev_list:
      self.addDev(dev)

  def set_instruction(self, instr):
    urjtag.chain.set_instruction(self, instr)
    # Set active_insteuction for the selected device
    self.devs[self.active_dev].active_instruction = instr

  def part(self, id):
    urjtag.chain.part(self, id)
    self.active_dev = id

  def tap_detect(self):
    # Capture output
    f = StringIO()
    with redirect_stdout(f):
      urjtag.chain.tap_detect(self)
    s = f.getvalue()
    f.close()
    return s


  def addDev(self, dev):
    # Add IR 
    ir_len = [r[1] for r in dev.registers if r[0] == "IR"][0]
    self.addpart(ir_len)
    self.part(len(self.devs))
    
    # Append to chain devices
    self.devs.append(dev) 
    
    # Add registers to UrJTAG
    for reg in dev.registers:
      # if reg[0] == 'BYPASS': continue
      self.add_register(reg[0], reg[1])

    # Add instructions to UrJTAG
    for inst in dev.instructions:
      if inst[0] == 'BYPASS': continue
      self.add_instruction(inst[0], inst[1], inst[2])

    # Set the instruction to Bypass just to be sure
    self.set_instruction('BYPASS')
    

  def __getitem__(self, id):
    return self.devs[id]
