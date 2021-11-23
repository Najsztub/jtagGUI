import wx
import wx.lib.mixins.listctrl as listmix
from Panels import panels, PinSetup

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
    for key, dut_pin in self.mainW.chain[self.active_dev].pins.items():
      self.m_pinList.InsertItem(index, key)
      self.m_pinList.SetItem(index, 1, dut_pin.port.name)
      if dut_pin.port.type != "":
        pin_type = dut_pin.port.type
        if not dut_pin.port.is_set:
          set_val = ''  
        elif dut_pin.write is not None:
          set_val = dut_pin.write
      else:
        pin_type = '-'
      
      if pin_type not in ['inout', 'out']:
        set_val = 'Not avaliable'
      
      
      self.m_pinList.SetItem(index, 2, pin_type)

      self.m_pinList.SetItem(index, 3, set_val)
      self.m_pinList.SetItemData(index, index)
      self.itemDataMap.append([key, dut_pin.port.name, pin_type, set_val])
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
    dev_port = dev.ports[port_name]
    
    # Do nothing if type linkage or missing
    if dev_port.type.lower() in ['-', 'linkage', 'in', '']: return

    # Show item popup menu and update selected value
    self.m_pinList.PopupMenu(PinSetup.PinSetup(dev, dev_port), event.GetPoint()) 
    set_item = self.m_pinList.GetItem(list_item_row, 3)
    if dev_port.is_set:
      set_item.SetText(dev_port.write)
    else: 
      set_item.SetText('')
    self.m_pinList.SetItem(set_item)