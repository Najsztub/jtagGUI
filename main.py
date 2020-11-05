import wx 
import wx.lib.mixins.listctrl as listmix
import math
import tatsu
import string
import re

import panels
from dut import DUT
import bsdl_parser
import urjtag_mock as urjtag
# import urjtag
from conf_tank import BSDLtank

#######################################################################
# Override UrJTAG class to include DUT processing
class JTAG(urjtag.chain):
  def __init__(self):
    #initialize parent class
    urjtag.chain.__init__(self)
    self.devs = []
  
  def addDevs(self, dev_list):
    for dev in dev_list:
      self.addDev(dev)

  def addDev(self, dev):
    # Add IR 
    ir_len = [r[1] for r in dev.registers if r[0] == "IR"][0]
    self.addpart(ir_len)
    self.part(len(self.devs))
    
    # Add registers to UrJTAG
    for reg in dev.registers:
      # if reg[0] == 'BYPASS': continue
      self.add_register(reg[0], reg[1])

    # Add instructions to UrJTAG
    for inst in dev.instructions:
      if inst[0] == 'BYPASS': continue
      self.add_instruction(inst[0], inst[1], inst[2])
    
    self.devs.append(dev) 

  def __getitem__(self, id):
    return self.devs[id]

#######################################################################
# Device mod dialog
class DefineDevice(panels.DefineDevice):
  #constructor
  def __init__(self,parent, dev):
    #initialize parent class
    panels.DefineDevice.__init__(self, parent)
    self.dev = dev
    # Fill registers and instructions
    for reg in self.dev.registers:
      self.m_reg_list.AppendItem([reg[0], str(reg[1])])
    for inst in self.dev.instructions:
      self.m_inst_list.AppendItem(inst)

  def regAdd( self, event ):
    self.m_reg_list.AppendItem(['', ''])

  def regDrop( self, event ):
    selected = self.m_reg_list.GetSelectedRow()
    reg = self.m_reg_list.GetItemData(selected)
    id = [i for i, r in self.dev.registers if r[0] == reg[0]]
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

  def defDone( self, event ):
    # TODO: Check if IR > 0
    self.result = None
    self.Destroy()

#######################################################################
# Override wxFormBuilder BottomPanel class
class BottomPanel(panels.BottomPanel):
  #constructor
  def __init__(self,parent):
    #initialize parent class
    panels.BottomPanel.__init__(self, parent)

#######################################################################
# Override wxFormBuilder LeftPanel class
class LeftPanel(panels.LeftPanel, listmix.ColumnSorterMixin):
  #constructor
  def __init__(self,parent):
    #initialize parent class
    panels.LeftPanel.__init__(self, parent)

    # Containers for devices
    self.active_dev = None
    self.itemDataMap = None
    self.rightP = None
    self.mainW = None

    # Add columns to list
    self.m_pinList.AppendColumn("Pin")
    self.m_pinList.AppendColumn("Name")
    self.m_pinList.AppendColumn("Type")

    # Add root to TreeList
    self.ch_root = self.m_chain.GetRootItem() # self.m_chain.InsertItem(self.m_chain.GetRootItem(), wx.dataview.TLI_FIRST, "JTAG chain")

    # Allow for column sorting
    listmix.ColumnSorterMixin.__init__(self, 3)
    self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.m_pinList)

  #----------------------------------------------------------------------
  # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
  def GetListCtrl(self):
    return self.m_pinList

  #----------------------------------------------------------------------
  def OnColClick(self, event):
    event.Skip()

  def dropDevs(self):
    # Drop dev panel devices
    self.m_chain.DeleteAllItems()
    self.ch_root = self.m_chain.GetRootItem() # self.m_chain.InsertItem(self.m_chain.GetRootItem(), wx.dataview.TLI_FIRST, "JTAG chain")
    # Drop pins
    self.m_pinList.DeleteAllItems()
    # Clear choice list
    self.m_dev_choice.Clear()

  def addDev(self, device):
    # Add BSR definition
    device.addCells()
    # Add devices to list 
    self.m_dev_choice.Append(device.name)
    # Add device to tree list
    child = self.m_chain.AppendItem(self.ch_root, "Device %s" % device.chain_id)
    self.m_chain.SetItemText(child, 1, device.name)

    # Add registers
    regs_parent = self.m_chain.AppendItem(child, "Registers")
    self.m_chain.SetItemText(regs_parent, 1, str(len(device.registers)))
    for reg in device.registers:
      reg_ch = self.m_chain.AppendItem(regs_parent, str(reg[0]))
      self.m_chain.SetItemText(reg_ch, 1, str(reg[1]))
    
    # Instructions
    inst_parent = self.m_chain.AppendItem(child, "Instructions")
    self.m_chain.SetItemText(inst_parent, 1, str(len(device.instructions)))
    for inst in device.instructions:
      inst_ch = self.m_chain.AppendItem(inst_parent, str(inst[0]))
      self.m_chain.SetItemText(inst_ch, 1, str(inst[1]))

  def selectDev(self, event):
    self.active_dev = self.m_dev_choice.GetSelection()
    self.rightP.dev = self.mainW.chain.devs[self.active_dev]

    # Select dev in UrJTAG
    self.mainW.chain.part(self.active_dev)

    # Add description in bottom status bar
    self.mainW.m_statusBar1.SetStatusText(', '.join([
      self.mainW.chain.devs[self.active_dev].name,
      self.mainW.chain.devs[self.active_dev].package
    ])) 

    # Refresh pin image
    self.rightP.Refresh()
    
    # Fill list with pin description
    self.m_pinList.DeleteAllItems()
    self.itemDataMap = [] 
    # Make sure that we have any pins
    if self.mainW.chain.devs[self.active_dev].pins is None: return
    index = 0
    for key, data in self.mainW.chain.devs[self.active_dev].pins.items():
      self.m_pinList.InsertItem(index, data['pin_id'])
      self.m_pinList.SetItem(index, 1, data['port_name'])
      if 'pin_type' in data:
        pin_type = data['pin_type']
      else:
        pin_type = '-'
      self.m_pinList.SetItem(index, 2, pin_type)
      self.m_pinList.SetItemData(index, key)
      self.itemDataMap.append([data['pin_id'], data['port_name'], pin_type])
      index += 1
    
  def getBSR(self, event):
    # Set IR to SAMPLE
    self.mainW.chain.part(self.active_dev)
    self.mainW.chain.set_instruction('SAMPLE')
    self.mainW.chain.shift_ir()
    # Get BSR from device and update rightP
    self.mainW.chain.shift_dr()
    bsr = self.mainW.chain.get_dr_out_string()
    self.mainW.chain[self.active_dev].parseBSR(bsr)
    # Refresh pin image
    self.rightP.Refresh()

#######################################################################
# Override BSDL repo dialog
class BSDLRepo(panels.BSDLRepo):
  #constructor
  def __init__(self,parent):
    panels.BSDLRepo.__init__(self, parent)
    self.parent = parent
    self.bsdl_repo = parent.bsdl_repo
    # Load data
    self.data = self.bsdl_repo.getTab()
    # Fill columns
    for row in self.data:
      self.m_bsdl_data.AppendItem(row[1:6])

  def addBSDL( self, event ):
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
      ast = self.parent.parser.parseBSDL(pathname)
    except IOError:
      wx.LogError("Cannot open file '%s'." % pathname)
      self.parent.log("Cannot open file '%s'." % pathname)
    except tatsu.exceptions.FailedToken:
      self.parent.log(', '.join(["BSDL error parsing ",  pathname]))
    if ast is not None:
      dev = DUT(ast)
      # Upload info to DB
      ret_data = self.bsdl_repo.addBSDL(dev.getID(), name=dev.name, source=pathname, ast=ast)
      # Add to self.data and table
      self.data.append(ret_data)
      self.m_bsdl_data.AppendItem(ret_data[1:6])

    openFileDialog.Destroy()

  def dropBSDL( self, event ):
    row = self.m_bsdl_data.GetSelectedRow()
    if row != wx.NOT_FOUND:
      self.bsdl_repo.delBSDL(self.data[row][0])
    self.m_bsdl_data.DeleteItem(row)
    del self.data[row]

#######################################################################
# Define Right panel class
class RightPanel(wx.Panel):
  """"""
  #----------------------------------------------------------------------
  def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="RightPanel"):
    super(RightPanel, self).__init__(parent, id, pos, size, style, name)
    
    self.dev = None
    self.leftP = None
    self.mainW = None

    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint) 
    self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

  def OnSize(self, event):
    event.Skip()
    self.Refresh()
  
  def OnPaint(self, e): 
    self.imgx, self.imgy = self.GetClientSize()
    dc =  wx.AutoBufferedPaintDC(self)
    brush = wx.Brush("white")  
    dc.SetBackground(brush)  
    dc.Clear() 
    
    # Skip if no pins present
    if self.dev is None or self.dev.pins is None: return

    pen = wx.Pen(wx.Colour(200,200,255)) 
    dc.SetPen(pen) 
    dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.TRANSPARENT)) 
    
    # Get device package and draw appropriate pins
    pkg = self.dev.package
    if bool(re.search("BGA", pkg)): self.plotBGA(dc, self.dev)
    else: self.plotTQFP(dc, self.dev)

  def plotPin(self, dc, pin, pt, width):
    # Set fill colour depending on Pin name
    pin_color = self.mainW.PIN_COLS['oth']
    if pin['port_name'] == 'VCC': pin_color = self.mainW.PIN_COLS['vcc']
    elif pin['port_name'] in ['GND', 'VSS']:  pin_color = self.mainW.PIN_COLS['gnd']
    elif pin['port_name'][0:2] == 'IO':  pin_color = self.mainW.PIN_COLS['io']
    dc.SetBrush(wx.Brush(pin_color, wx.BRUSHSTYLE_SOLID))

    # Plot pin square
    dc.DrawRectangle(pt[0], pt[1], width, width) 

    # Draw state
    if 'read' in pin and pin['read'] != '':
      state_col = self.mainW.PIN_COLS['io_z']
      if pin['read'] == '0': state_col = self.mainW.PIN_COLS['io_0']
      elif pin['read'] == '1': state_col = self.mainW.PIN_COLS['io_1']
      
      # Draw circle 
      dc.SetBrush(wx.Brush(state_col, wx.BRUSHSTYLE_SOLID))
      dc.DrawCircle(pt[0] + 0.5 * width, pt[1] + 0.5 * width, 0.3 * width)
  
  def plotTQFP(self, dc, dev):
    npins = len(dev.pins)
    side = math.ceil(npins / 4)
    pt_dir = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    rec_b = min(self.imgx, self.imgy) * .8 / side
    pin_w = math.floor(rec_b)
    border = min(self.imgx, self.imgy) * 0.1
    coord = [border, border]
    for i in range(npins):
      loc_dir = pt_dir[math.floor(i / side)]
      # Search for item based on on pin nr
      # it = next((i for i, item in enumerate(dev.pins) if dev.pins.["name"] == "Pam"), None)
      try:
        it = dev.pins[dev.pin_dict[str(i+1)]]
      except KeyError:
        it = {'port_name': 'GND', 'pin_type': 'GND', 'read': ''}
      # Draw rectangles for pins
      # Move pins 1 unit, so they do not overlap in corners
      if ( math.floor(i / side) == 2):
        pt = [math.floor(coord[0] + rec_b), math.floor(coord[1] - rec_b)]
      elif (math.floor(i / side) == 1):
        pt = [math.floor(coord[0] + rec_b), math.floor(coord[1])]
      elif (math.floor(i / side) == 3):
        pt = [math.floor(coord[0]), math.floor(coord[1] - rec_b)]
      else:
        pt = [math.floor(coord[0]), math.floor(coord[1])]
      
      # Increment coords
      coord[0] += rec_b * loc_dir[0]
      coord[1] += rec_b * loc_dir[1]
      
      # Draw pin
      self.plotPin(dc, it, pt, pin_w)

  def plotBGA(self, dc, dev):
    npins = len(dev.pins)
    side = math.ceil(math.sqrt(npins))
    chars = [char for char in string.ascii_uppercase if char not in 'IOQS']
    rec_b = min(self.imgx, self.imgy) * .8 / side
    pin_w = math.floor(rec_b)
    border = min(self.imgx, self.imgy) * 0.1
    # Set font
    font = wx.Font(math.floor(rec_b*0.5), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.SetFont(font) 
    for i in range(side):
      # Row pin nr
      dc.DrawText(chars[i], border - rec_b, math.ceil(rec_b * i + border))
      for j in range(side):
        # Col pin nr
        if i == 0: dc.DrawText(str(j+1), math.ceil(rec_b * j + border), border - rec_b)
        it = dev.pins[dev.pin_dict[chars[i] + str(j+1)]]
        # Draw pin
        pt =[math.ceil(border + rec_b * j), math.ceil(border + rec_b* i)]

        # Draw pin
        self.plotPin(dc, it, pt, pin_w)

#######################################################################
# Main window class
class Mywin(panels.MainFrame): 
  def __init__(self, parent, title, parser = None): 
    panels.MainFrame.__init__(self, parent)  

    self.parser = parser
 
    # Add JTAG chain container
    self.chain = None

    # Add BSDL Repo
    self.bsdl_repo = BSDLtank('bsdl/bsdl_repo.sqlite')

    self.PIN_COLS = {
      'vcc': wx.Colour(255,0,0),
      'gnd': wx.Colour(10,10,10),
      'io' : wx.Colour(240,240,240),
      'oth' : wx.Colour(150,150,220),
      'io_1': wx.Colour(200,0 , 0),
      'io_0': wx.Colour(255,255,255),
      'io_z': wx.Colour(128, 128, 128)
    }

    # Split panels
    splitMain = wx.SplitterWindow(self)
    splitV = wx.SplitterWindow(splitMain)

    # Create top L&R panels
    self.leftP = LeftPanel(splitV)
    self.rightP = RightPanel(splitV)

    # Add pointer to left panel
    self.leftP.mainW = self
    self.leftP.rightP = self.rightP

    # Add pointer to right panel
    self.rightP.mainW = self
    self.rightP.rightP = self.leftP

    # split the top window
    splitV.SplitVertically(self.leftP, self.rightP)
    splitV.SetSashGravity(0.1)

    # Add bottom panel
    self.bottomP = BottomPanel(splitMain)
    splitMain.SplitHorizontally(splitV, self.bottomP)
    splitMain.SetSashGravity(0.9)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(splitMain, 1, wx.EXPAND)
    self.SetSizer(sizer)

    # wxFormBuilder generated code

    self.Show(True)
    
  #----------------------------------------------------------------------
  def editBSDLrepo(self, event):
    dlg = BSDLRepo(self)
    dlg.Show(True)
  
  #----------------------------------------------------------------------
  def loadFile(self, event):
    # BSDL file loading dialog
    openFileDialog = wx.FileDialog(self, "Open", "", "", 
                                    "BSDL files (*.bsdl, *.bsd)|*.bsdl;*.bsd|All files (*.*)|*.*", 
                                    wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if openFileDialog.ShowModal() == wx.ID_CANCEL:
      return     # the user changed their mind
    # Proceed loading the file chosen by the user
    pathname = openFileDialog.GetPath()
    try:
      self.log("Reading '%s'." % pathname)
      self.loadBSDL(pathname)
    except IOError:
      wx.LogError("Cannot open file '%s'." % pathname)
      self.log("Cannot open file '%s'." % pathname)
    openFileDialog.Destroy()

  def loadBSDL(self, file):
    # Parse BSDL file
    try:
      ast = self.parser.parseBSDL(file)
      dev = DUT(ast)
      # self.addDev(dev)
      self.m_statusBar1.SetStatusText(file, 1) 
    except tatsu.exceptions.FailedToken:
      self.log(', '.join(["BSDL error parsing ",  file]))  

  def selectDev(self, devid):
    # Select device in main window
    self.m_statusBar1.SetStatusText(', '.join([
      self.chain.devs[devid].name,
      self.chain.devs[devid].package
    ])) 

  def dropChain(self, event):
    del self.chain 
    self.m_scan_tap.Disable()
  
  def attachChain(self, event):
    cid = self.m_cable.GetSelection()
    if cid <= 0:
      wx.MessageBox("Please select a UrJTAG cable", caption="Invalid cable",
              style=wx.OK|wx.CENTRE)
      return
    self.chain = JTAG()
    self.chain.cable(self.m_cable.GetString(cid))
    self.m_scan_tap.Enable()

  def scanTAP(self, event):
    # Scan the chain and populate window with found devices
    self.chain.tap_detect()
    found_chain = self.chain.len()
    if found_chain <= 0:
      self.log("No devices found.")
      return
    if found_chain > 1: self.log("Found %s devices." % found_chain)
    else: self.log("Found %s device." % found_chain)
    # TODO: Clear leftP lists
    self.leftP.dropDevs()
    # Get ids and search in DB
    ids = ["{0:b}".format(self.chain.partid(id)).zfill(32) for id in range(found_chain)]
    # Reset chain
    del self.chain
    self.chain = JTAG()
    self.chain.cable(self.m_cable.GetString(self.m_cable.GetSelection()))

    # Fill devices
    for dev_code in ids:
      # Populate app with devices
      dev = DUT(idcode=dev_code)
      dev.chain_id = len(self.chain.devs)
      # Search for IDCODE in DB
      db_bsdl = self.bsdl_repo.getCodes(dev_code)
      if db_bsdl is not None and db_bsdl[1] is not None:
        dev.addAST(db_bsdl[1])
        dev.inner_id = db_bsdl[0]
      else:
        # No IR found, so we need to provide it manually
        dev.idcode = dev_code
        dev.addRegisters('IDCODE', 32)
        dev.addRegisters('IR', 0)
        # dev.addInstructions('BYPASS', '1', 'BYPASS')
        dev.name = "Unknown (%s)" % len(self.chain.devs)
        self.askDevice(dev)
        self.log("Unknown device IDCODE: %s" % dev_code)
      # Notice widgets about new device
      self.addDevice(dev)

  def addDevice(self, dev):
    # Add device to list
    self.chain.addDev(dev)
    # Append device to left panel
    self.leftP.addDev(dev)


  def askDevice(self, dev):
    with DefineDevice(self, dev) as dlg:
      dlg.ShowModal()

  def OnExit(self, evt):
    self.Close(True)  

  def log(self, txt):
    self.bottomP.m_textCtrl1.AppendText(txt + '\n')


if __name__ == "__main__":
  bsdl_parser = bsdl_parser.Parser('bsdl.ebnf')
  ex = wx.App() 
  Mywin(None,'JTAG Viewer', parser=bsdl_parser) 
  ex.MainLoop()