import wx 
import wx.lib.mixins.listctrl as listmix
import math
import tatsu
import string
import re
from datetime import datetime
# For showing stdout from UrJTAG in log
# https://stackoverflow.com/questions/5136611/capture-stdout-from-a-script
from contextlib import redirect_stdout
from io import StringIO

import panels
from dut import DUT
import bsdl_parser
import urjtag_mock as urjtag
# import urjtag
from conf_tank import BSDLtank, CABLES_DICT

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

#######################################################################
# Pin popup menu
class PinSetup(wx.Menu):
  def __init__(self, device, port):
    super(PinSetup, self).__init__()
      
    self.device = device
    self.port = port

    high = wx.MenuItem(self, wx.ID_ANY, 'High 1')
    self.Append(high)
    self.Bind(wx.EVT_MENU, self.PinHigh, high)

    low = wx.MenuItem(self, wx.ID_ANY, 'Low 0')
    self.Append(low)
    self.Bind(wx.EVT_MENU, self.PinLow, low)

    reset = wx.MenuItem(self, wx.ID_ANY, 'Reset')
    self.Append(reset)
    self.Bind(wx.EVT_MENU, self.PinReset, reset)

  def PinHigh(self, e):
    self.device.setPort(self.port, 'write', '1')

  def PinLow(self, e):
    self.device.setPort(self.port, 'write', '0')
    
  def PinReset(self, e):
    self.device.setPort(self.port, 'write', '')
        

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
    self.m_pinList.AppendColumn("Set")

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
    self.ch_root = self.m_chain.GetRootItem() 
    # Drop pins
    self.m_pinList.DeleteAllItems()
 
  def addDev(self, device):
    # Add BSR definition
    device.addCells()
    # Add device to tree list
    child = self.m_chain.AppendItem(self.ch_root, "Device %s" % device.chain_id)
    self.m_chain.SetItemText(child, 2, device.name)

    # Add registers
    regs_parent = self.m_chain.AppendItem(child, "Registers")
    self.m_chain.SetItemText(regs_parent, 2, str(len(device.registers)))
    for reg in device.registers:
      reg_ch = self.m_chain.AppendItem(regs_parent, str(reg[0]))
      self.m_chain.SetItemText(reg_ch, 2, str(reg[1]))
    
    # Instructions
    inst_parent = self.m_chain.AppendItem(child, "Instructions")
    self.m_chain.SetItemText(inst_parent, 2, str(len(device.instructions)))
    for inst in device.instructions:
      inst_ch = self.m_chain.AppendItem(inst_parent, str(inst[0]))
      self.m_chain.SetItemText(inst_ch, 2, str(inst[1]))
      if str(inst[0]) == 'BYPASS': self.m_chain.SetItemText(inst_ch, 1, '<')

  def instSet(self, event):
    self.propCheck(event, True)

  def propCheck(self, event=None, iset=False):
    # check if new device and switch
    inst_item = event.GetItem()
    path = []
    # Loop until root to find path
    while inst_item.IsOk():
      path.append(inst_item)
      inst_item = self.m_chain.GetItemParent(inst_item)
    # Get last-1 item, which holds the dev id
    chk_dev = path[len(path) - 2]
    dev_name = self.m_chain.GetItemText(chk_dev, 0)  
    dev_id = int(dev_name.split(' ')[1])
    if dev_id != self.active_dev:
      self.selectDev(active_dev=dev_id)
    # If in Instructions, select new instruction
    # Check if path[1] is an instruction
    if iset == False or len(path) < 4 or self.m_chain.GetItemText(path[1], 0) != 'Instructions': return
    # Continue otherwise
    # Clear inst indicator
    iit = self.m_chain.GetFirstChild(path[1])
    while iit.IsOk():
      self.m_chain.SetItemText(iit, 1, '') 
      iit = self.m_chain.GetNextSibling(iit)
    # Set active instruction for the device
    instr = self.m_chain.GetItemText(path[0], 0)
    self.mainW.chain.part(self.active_dev)
    self.mainW.chain.set_instruction(instr)
    # Set instr indicator
    self.m_chain.SetItemText(path[0], 1, '<')
    self.m_bt_shift_ir.SetLabel('< Shift IR')

  def selectDev(self, event=None, active_dev=None):
    if active_dev is not None: self.active_dev = active_dev
    self.rightP.setDevice(self.mainW.chain.devs[self.active_dev])

    # Select dev in UrJTAG
    self.mainW.chain.part(self.active_dev)

    # Decide if BSR/other and act accordingly
    if self.mainW.chain[self.active_dev].bsr_cells is not None:
      dr = self.mainW.chain.get_dr_out_string()
      if len(dr) == self.mainW.chain[self.active_dev].regLen('BSR'):      
        self.mainW.chain[self.active_dev].parseBSR(dr)

    # Refresh pin image
    self.rightP.Refresh()
    
    # Add description in bottom status bar
    self.mainW.m_statusBar1.SetStatusText(', '.join([
      self.mainW.chain[self.active_dev].name,
      self.mainW.chain[self.active_dev].package
    ])) 

    # Fill list with pin description
    self.m_pinList.DeleteAllItems()
    self.itemDataMap = [] 
    
    # Make sure that we have any pins
    if self.mainW.chain[self.active_dev].pins is None: return
    index = 0
    for key, data in self.mainW.chain[self.active_dev].pins.items():
      self.m_pinList.InsertItem(index, data['pin_id'])
      self.m_pinList.SetItem(index, 1, data['port_name'])
      if 'pin_type' in data:
        pin_type = data['pin_type']
      else:
        pin_type = '-'
      self.m_pinList.SetItem(index, 2, pin_type)
      if 'write' in data:
        set_val = data['write']
      else: set_val = ''
      self.m_pinList.SetItem(index, 3, set_val)
      self.m_pinList.SetItemData(index, key)
      self.itemDataMap.append([data['pin_id'], data['port_name'], pin_type, set_val])
      index += 1
    
  def shiftIR(self, event):
    self.mainW.shiftIR(event)

  def shiftDR(self, event):
    self.mainW.shiftDR(event)

  def pinListRight(self, event):
    # TODO: Allow for multiple pin selection and setting
    # Pin right click
    dev = self.mainW.chain[self.active_dev]
    list_item_row = event.GetIndex()
    port_name = self.m_pinList.GetItem(list_item_row, 1).GetText()
    dev_port = dev.pins[dev.port_map[port_name][0]]
    
    # Do nothing if type linkage or missing
    if dev_port['pin_type'].lower() in ['-', 'linkage']: return

    # Show item popup menu and update selected value
    self.m_pinList.PopupMenu(PinSetup(dev, port_name), event.GetPoint()) 
    set_item = self.m_pinList.GetItem(list_item_row, 3)
    set_item.SetText(dev_port['write'])
    self.m_pinList.SetItem(set_item)

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

  def addBSDL( self, event=None):
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
      ret_data = self.bsdl_repo.addBSDL(dev.getBSDL_IDCODE(), name=dev.name, source=pathname, ast=ast)
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

    self.npins =  None
    self.package = None
  
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint) 
    self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

  def setDevice(self, dev):
    self.dev = dev
    # Try to get number of pins from the package description
    # Sometimes pins are not described and we end up with holes
    if dev.pins is None:
      self.npins = None
      return
    p_pins = re.search("[0-9]+$", dev.package)
    if p_pins is not None:
      self.npins = int(p_pins[0])
    else:
      self.npins = len(dev.pins)

  def OnSize(self, event):
    event.Skip()
    self.Refresh()

  # TODO: Add selected pin highligth
  # TODO: Add TQFP pin nr & labels
  # TODO: Add pin menu/panel
  
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
    if bool(re.search("BGA", pkg)): self.plotBGA(dc)
    else: self.plotTQFP(dc)

  def plotPin(self, dc, pin, pt, width):
    # TODO: Include write state in the picture
    # Set fill colour depending on Pin name
    pin_color = self.mainW.PIN_COLS['oth']
    port = pin['port_name']
    if port[0:3] == 'VCC': pin_color = self.mainW.PIN_COLS['vcc']
    elif port[0:3] in ['GND', 'VSS']:  pin_color = self.mainW.PIN_COLS['gnd']
    elif port[0:2] == 'IO':  pin_color = self.mainW.PIN_COLS['io']
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
      dc.DrawCircle(int(pt[0] + 0.5 * width), int(pt[1] + 0.5 * width), int(0.3 * width))
  
  def plotTQFP(self, dc):
    side = math.ceil(self.npins / 4)
    pt_dir = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    rec_b = min(self.imgx, self.imgy) * .8 / side
    pin_w = math.floor(rec_b)
    border = min(self.imgx, self.imgy) * 0.1
    coord = [border, border]
    for i in range(self.npins):
      loc_dir = pt_dir[math.floor(i / side)]
      # Search for item based on on pin nr
      try:
        it = self.dev.pins[self.dev.pin_dict[str(i+1)]]
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

  def plotBGA(self, dc):
    side = math.ceil(math.sqrt(self.npins))
    chars = [char for char in string.ascii_uppercase if char not in 'IOQS']
    rec_b = min(self.imgx, self.imgy) * .8 / side
    pin_w = math.floor(rec_b)
    border = min(self.imgx, self.imgy) * 0.1
    # Set font
    font = wx.Font(math.floor(rec_b*0.5), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.SetFont(font) 
    for i in range(side):
      # Row pin nr
      dc.DrawText(chars[i], int(border - rec_b), math.ceil(rec_b * i + border))
      for j in range(side):
        # Col pin nr
        if i == 0: dc.DrawText(str(j+1), math.ceil(rec_b * j + border), int(border - rec_b))
        it = self.dev.pins[self.dev.pin_dict[chars[i] + str(j+1)]]
        # Draw pin
        pt =[math.ceil(border + rec_b * j), math.ceil(border + rec_b* i)]

        # Draw pin
        self.plotPin(dc, it, pt, pin_w)

#######################################################################
# Main window class
class Mywin(panels.MainFrame): 
  def __init__(self, parent, title, parser = None): 
    panels.MainFrame.__init__(self, parent)  

    # Set timer period to OFF :0 
    self.dr_auto = 0
    self.dr_auto_timer = None

    # Setup BSDL parser
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

    # Populate with cables 
    for c in CABLES_DICT:
      self.m_cable.Append(c)

    # Add defult cable if in settings
    cable = self.bsdl_repo.getSetting('cable.name')
    if cable is not None:
      # Select default cable and params
      cab_name = self.m_cable.FindString(cable[0])
      self.m_cable.SetSelection(cab_name)
      cab_params = self.bsdl_repo.getSetting('cable.params')
      if cab_params is not None:
        self.m_cable_params.SetValue(cab_params[0])

    # wxFormBuilder generated code
    self.Show(True)

  def saveCable(self, event):
    cid = self.m_cable.GetSelection()
    if cid <= 0:
      wx.MessageBox("Please select a UrJTAG cable", caption="Invalid cable",
              style=wx.OK|wx.CENTRE)
      return
    self.bsdl_repo.setSetting('cable.name', self.m_cable.GetString(cid))
    self.bsdl_repo.setSetting('cable.params', self.m_cable_params.GetValue())
    self.log("Cable %s saved as default." % self.m_cable.GetString(cid))
    
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
    # Stop timer
    if self.dr_auto_timer is not None: 
      self.dr_auto_timer.Stop()
    self.dr_auto = 0
    # Select OFF timer
    timer_items = self.m_mauto.GetMenuItems()
    for mit in timer_items:
      if mit is timer_items[len(timer_items) - 1]:
        mit.Check(True)
      elif mit.IsCheckable():
        mit.Check(False)
    # Clear rightP
    self.rightP.dev = None
    self.rightP.Refresh()
    # Clear left panel
    self.leftP.active_dev = None
    self.leftP.dropDevs()

    del self.chain 
    self.m_scan_tap.Disable()
  
  def attachChain(self, event):
    cid = self.m_cable.GetSelection()
    if cid <= 0:
      wx.MessageBox("Please select a UrJTAG cable", caption="Invalid cable",
              style=wx.OK|wx.CENTRE)
      return
    self.chain = JTAG()
    cable_args = [self.m_cable.GetString(cid)]
    # Add arguments in case self.m_cable_params is not emply
    opt_args = self.m_cable_params.GetValue()
    if opt_args != '':
      arg_list = re.findall("[^\s]+", re.sub("\s*=\s*", "=", opt_args))
      cable_args += arg_list
    self.chain.cable(*cable_args)
    self.m_scan_tap.Enable()

  def scanTAP(self, event):
    # Scan the chain and populate window with found devices
    msg = self.chain.tap_detect()
    if len(msg) > 0: self.log(msg, prefix='UrJTAG')
    found_chain = self.chain.len()
    if found_chain <= 0:
      self.log("No devices found.")
      return
    if found_chain > 1: self.log("Found %s devices." % found_chain)
    else: self.log("Found %s device." % found_chain)
    # Clear leftP lists
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
        self.log("Unknown device IDCODE: %s" % dev_code)
        # No IR found, so we need to provide it manually
        dev.idcode = dev_code
        dev.addRegisters('IDCODE', 32)
        dev.addRegisters('IR', 0)
        dev.addInstructions('BYPASS', '1', 'BYPASS')
        dev.name = "Unknown (%s)" % len(self.chain.devs)
        # Ask for IR len
        with DefineDevice(self, dev, found_chain) as dlg:
          dlg.ShowModal()
      # Notice widgets about new device
      self.addDevice(dev)

  def addDevice(self, dev):
    # Add device to list
    self.chain.addDev(dev)
    # Append device to left panel
    self.leftP.addDev(dev)

  def shiftIR(self, event):
    self.chain.shift_ir()
    self.leftP.m_bt_shift_ir.SetLabel('Shift IR')
    # Add time to log
    self.log('IR shifted')

  def shiftDR(self, event=None):
    #  BSR out values
    active = self.leftP.active_dev
    self.chain.part(active)
    # Check if we have BSR cells defined
    if self.chain[active].bsr_cells is None: return
    in_bsr = self.chain[active].setBSR()
    if in_bsr[0] > 0:
      self.chain.set_dr_in(in_bsr[1])

    # Get BSR from device and update rightP
    self.chain.shift_dr()

    # Decide if BSR/other and act accordingly
    dr = self.chain.get_dr_out_string()
    if len(dr) == self.chain[active].regLen('BSR'):      
      self.chain[active].parseBSR(dr)
      # Refresh pin image
      self.rightP.Refresh()
    else:
      self.log('DR: ' + dr)

  def dr_timer_chng(self, event):
    # Exit if no devices
    if len(self.chain.devs) <= 0: return
    # Define changing DR update timer period
    widget = event.GetEventObject()
    # Search in menu objects
    caller = self.m_mauto.FindChildItem(event.GetId())
    pos = caller[1]
    if pos is None: return
    # Set timer depending on selected menu item
    elif pos == 0:
      # 1s
      self.dr_auto = 1000
    elif pos == 1:
      # 1/2s
      self.dr_auto = 500
    elif pos == 2:
      # 1/4s
      self.dr_auto = 250
    elif pos == 3:
      # 1/8s
      self.dr_auto = 125
    elif pos == 5:
      # Turn off
      self.dr_auto = 0

    # Setup checks in menu
    for mit in self.m_mauto.GetMenuItems():
      if mit is caller[0]:
        mit.Check(True)
      elif mit.IsCheckable():
        mit.Check(False)
    
    # Call timer
    if self.dr_auto_timer is not None: 
      self.dr_auto_timer.Stop()
    self.dr_timer()


  def dr_timer(self):
    # Stop timer if self.dr_auto is 0
    if self.dr_auto == 0: return

    # call shitfDR
    self.shiftDR()

    # Call timer after self.dr_auto ms
    if self.dr_auto_timer is None:
      self.dr_auto_timer = wx.CallLater(self.dr_auto, self.dr_timer)
    else:
      self.dr_auto_timer.Start(self.dr_auto)

  def OnExit(self, evt):
    self.Close(True)  

  def log(self, txt, prefix=''):
    if prefix != '':
      line = '{0}: {1}\n{2}\n'.format(str(datetime.now()).split('.')[0], prefix, txt)
    else:
      line = '{0}: {1}\n'.format(str(datetime.now()).split('.')[0],  txt)
    self.bottomP.m_textCtrl1.AppendText(line)


if __name__ == "__main__":
  bsdl_parser = bsdl_parser.Parser('bsdl.ebnf')
  ex = wx.App() 
  Mywin(None,'JTAG Viewer', parser=bsdl_parser) 
  ex.MainLoop()