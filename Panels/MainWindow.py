import wx
import tatsu
import re
from datetime import datetime

import Panels.panels as panels

from Panels.LeftPanel import LeftPanel
from Panels.RightPanel import RightPanel
from Panels.BSDLRepo import BSDLRepo
from Panels.BottomPanel import BottomPanel
from Panels.DefineDevice import DefineDevice

from HWLayer.JTAG import JTAG
from HWLayer.dut import DUT

from HWLayer.conf_tank import BSDLtank, CABLES_DICT


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
      'jtag' : wx.Colour(255, 204, 102),
      'oth' : wx.Colour(150,150,220),
      'nc' : wx.Colour(255, 255, 255),
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
    # Compile BSDL parser if not initialized
    if not self.parent.parser.initialized:
      self.parent.log("Initializing BSDL parser. Might take about a minute.")
      self.parent.parser.initialize()
      self.parent.log("DONE Initializing BSDL parser.")
    try:
      self.parent.log("Try parsing BSDL file.")
      ast = self.parser.parseBSDL(file)
      self.parent.log("Parsing DONE.")
      dev = DUT(ast)
      # self.addDev(dev)
      self.m_statusBar1.SetStatusText(file, 1) 
    except tatsu.exceptions.FailedToken as ex:
      self.parent.log(f"BSDL error parsing {file}")
      self.parent.log(ex)

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
