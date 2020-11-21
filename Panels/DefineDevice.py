import wx
import tatsu
from Panels import panels

from HWLayer.dut import DUT

#######################################################################
# Device mod dialog
class DefineDevice(panels.DefineDevice):
  #constructor
  def __init__(self,parent, dev, chain_length):
    
    #initialize parent class
    panels.DefineDevice.__init__(self, parent)
    title = 'Define unknown Device {} / {}, IDCODE: 0x{:02X}'.format(dev.chain_id+1, chain_length, int(dev.idcode, 2))
    self.SetTitle(title)
    
    self.mainW = parent

    self.dev = dev

    self.fillProps()
    
  def fillProps(self):
    # Fill registers and instructions
    self.m_reg_list.DeleteAllItems()
    for reg in self.dev.registers:
      self.m_reg_list.AppendItem([reg[0], str(reg[1])])
    self.m_inst_list.DeleteAllItems()
    for inst in self.dev.instructions:
      self.m_inst_list.AppendItem(inst)

  def regAdd( self, event ):
    self.m_reg_list.AppendItem(['', ''])

  def regDrop( self, event ):
    selected = self.m_reg_list.GetSelectedRow()
    reg = self.m_reg_list.GetTextValue(selected,0)
    id = [i for i, r in enumerate(self.dev.registers) if r[0] == reg]
    if len(id) != 0:
      del self.dev.registers[id[0]]
    self.m_reg_list.DeleteItem(selected)

  def regChange( self, event ):
    current = self.m_reg_list.GetSelectedRow()
    reg = [self.m_reg_list.GetTextValue(current,col) for col in range(2)]
    # Stop if empty
    if reg == '': return
    # Find id and update if exists or add
    id = [i for i, r in enumerate(self.dev.registers) if r[0] == reg[0]]
    if len(id) == 0:
      self.dev.addRegisters(reg[0], reg[1])
    else: 
      self.dev.registers[id[0]][1] = int(reg[1])

  def instAdd( self, event ):
    self.m_inst_list.AppendItem(['', '', ''])

  def instDrop( self, event ):
    selected = self.m_inst_list.GetSelectedRow()
    inst = self.m_inst_list.RowToItem(selected).value
    id = [i for i, r in self.dev.instructions if r[0] == inst[0]]
    if len(id) != 0:
      del self.dev.instructions[id[0]]
    self.m_inst_list.DeleteItem(selected)

  def instChange( self, event ):
    current = self.m_inst_list.GetSelectedRow()
    inst = [self.m_inst_list.GetTextValue(current,col) for col in range(3)]
    # Stop if empty
    if inst == '': return
    # Find id and update if exists or add
    id = [i for i, r in enumerate(self.dev.instructions) if r[0] == inst[0]]
    if len(id) == 0:
      self.dev.addInstructions(inst[0], inst[1], inst[2])
    else: 
      self.dev.instructions[id[0]][1] = inst[1]
      self.dev.instructions[id[0]][2] = inst[2]

  def importBSDL(self, event):
    # Add device from BSDL
    # BSDL file loading dialog
    openFileDialog = wx.FileDialog(self, "Open", "", "", 
                                    "BSDL files (*.bsdl, *.bsd)|*.bsdl;*.bsd|All files (*.*)|*.*", 
                                    wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if openFileDialog.ShowModal() == wx.ID_CANCEL:
      return     # the user changed their mind
    # Proceed loading the file chosen by the user
    pathname = openFileDialog.GetPath()
    ast = None
    try:
      ast = self.mainW.parser.parseBSDL(pathname)
    except IOError:
      wx.LogError("Cannot open file '%s'." % pathname)
    except tatsu.exceptions.FailedToken:
      self.mainW.log(', '.join(["BSDL error parsing ",  pathname]))
    if ast is None:
      wx.LogError("Could not parse BSDL definitions!")
      openFileDialog.Destroy()
      return
    bsdl_dev = DUT(ast)
    # Check if ID codes match
    if bsdl_dev.cmpID(self.dev.idcode):
      # We have a match!
      # Update dev with new values
      self.dev.addAST(ast)
      # Parse and fill props
      self.fillProps()
      # Add to BSDL repository
      self.mainW.bsdl_repo.addBSDL(bsdl_dev.getBSDL_IDCODE(), name=bsdl_dev.name, source=pathname, ast=ast)
      self.mainW.log('Added %s to BSDL repository' % bsdl_dev.name)
      pass
    else:
      cmp = '0x{:02X} != 0b{}'.format(int(self.dev.idcode, 2), bsdl_dev.idcode)
      wx.LogError("Device IDCODE does not match BSDL definition!\n" + cmp)
    # Destroy dialog box
    openFileDialog.Destroy()

  def defDone( self, event ):
    # Check if IR > 0
    ir = [r for r in self.dev.registers if r[0] == 'IR']
    if len(ir) == 0 or ir[0][1] <= 0:
      wx.MessageBox(
        "Please provide a valid (>0) IR length", caption="Invalid IR length",
        style=wx.OK|wx.CENTRE)
      return
    self.result = None
    self.Destroy()
