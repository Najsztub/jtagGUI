import wx 
import wx.lib.mixins.listctrl as listmix
import math
import tatsu
import string
import re

import panels
from dut import DUT
import bsdl_parser

#######################################################################



#inherit from the MainFrame created in wxFormBuilder and create janelaPrincipal
class BottomPanel(panels.BottomPanel):
  #constructor
  def __init__(self,parent):
    #initialize parent class
    panels.BottomPanel.__init__(self, parent)

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

  def addDev(self, device):
    # Add devices to list 
    self.m_dev_choice.Append(device.name)

  def selectDev(self, event):
    self.active_dev = self.m_dev_choice.GetSelection()
    self.rightP.dev = self.mainW.devs[self.active_dev]
    self.m_pinList.DeleteAllItems()
    self.itemDataMap = [] 
    index = 0
    for key, data in self.mainW.devs[self.active_dev].pins.items():
      self.m_pinList.InsertItem(index, data['pin_id'])
      self.m_pinList.SetItem(index, 1, data['name'])
      if 'pin_type' in data:
        pin_type = data['pin_type']
      else:
        pin_type = '-'
      self.m_pinList.SetItem(index, 2, pin_type)
      self.m_pinList.SetItemData(index, key)
      self.itemDataMap.append([data['pin_id'], data['name'], pin_type])
      index += 1
    self.rightP.Refresh()

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
    if self.dev is None: return

    pen = wx.Pen(wx.Colour(0,0,255)) 
    dc.SetPen(pen) 
    dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.TRANSPARENT)) 
    # for dev in self.dev:
    pkg = self.dev.package
    if bool(re.search("BGA", pkg)): self.plotBGA(dc, self.dev)
    else: self.plotTQFP(dc, self.dev)
  
  def plotTQFP(self, dc, dev):
    npins = len(dev.pins)
    side = math.ceil(npins / 4)
    pt_dir = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    rec_b = min(self.imgx, self.imgy) * .8 / side
    border = min(self.imgx, self.imgy) * 0.1
    coord = [border, border]
    for i in range(npins):
      loc_dir = pt_dir[math.floor(i / side)]
      # Search for item based on on pin nr
      # it = next((i for i, item in enumerate(dev.pins) if dev.pins.["name"] == "Pam"), None)
      it = dev.pins[dev.pin_dict[str(i+1)]]

      # Set fill colour depending on Pin name
      pin_color = self.mainW.PIN_COLS['oth']
      if it['name'] == 'VCC': pin_color = self.mainW.PIN_COLS['vcc']
      elif it['name'] == 'GND':  pin_color = self.mainW.PIN_COLS['gnd']
      elif it['name'][0:2] == 'IO':  pin_color = self.mainW.PIN_COLS['io']
      dc.SetBrush(wx.Brush(pin_color, wx.BRUSHSTYLE_SOLID))

      # Draw rectangles for pins
      # Move pins 1 unit, so they do not overlap in corners
      if ( math.floor(i / side) == 1):
        dc.DrawRectangle(math.floor(coord[0]), math.floor(coord[1] +  rec_b), math.floor(rec_b), math.floor(rec_b)) 
      elif (math.floor(i / side) == 2):
        dc.DrawRectangle(math.floor(coord[0] - rec_b), math.floor(coord[1] +  rec_b), math.floor(rec_b), math.floor(rec_b)) 
      elif (math.floor(i / side) == 3):
        dc.DrawRectangle(math.floor(coord[0] - rec_b), math.floor(coord[1]), math.floor(rec_b), math.floor(rec_b)) 
      else:
        dc.DrawRectangle(math.floor(coord[0]), math.floor(coord[1]), math.floor(rec_b), math.floor(rec_b)) 
      # Increment coords
      coord[0] += rec_b * loc_dir[0]
      coord[1] += rec_b * loc_dir[1]

  def plotBGA(self, dc, dev):
    npins = len(dev.pins)
    side = math.ceil(math.sqrt(npins))
    chars = [char for char in string.ascii_uppercase if char not in 'IOQS']
    rec_b = min(self.imgx, self.imgy) * .8 / side
    border = min(self.imgx, self.imgy) * 0.1
    for i in range(side):
      for j in range(side):
        it = dev.pins[dev.pin_dict[chars[i] + str(j+1)]]
        # Set pin color
        pin_color = self.mainW.PIN_COLS['oth']
        if it['name'] == 'VCC': pin_color = self.mainW.PIN_COLS['vcc']
        elif it['name'] == 'GND':  pin_color = self.mainW.PIN_COLS['gnd']
        elif it['name'][0:2] == 'IO':  pin_color = self.mainW.PIN_COLS['io']
        dc.SetBrush(wx.Brush(pin_color, wx.BRUSHSTYLE_SOLID)) 
        # Draw pin
        dc.DrawRectangle(border + math.ceil(rec_b * i), border + math.floor(rec_b* j), math.floor(rec_b), math.floor(rec_b)) 


class Mywin(wx.Frame): 

  def __init__(self, parent, title, parser = None): 
    super(Mywin, self).__init__(parent, title = title,size = (640,480))  

    self.parser = parser
    self.devs = []
    self.InitUI() 

    self.PIN_COLS = {
      'vcc': wx.Colour(255,0,0),
      'gnd': wx.Colour(10,10,10),
      'io' : wx.Colour(240,240,240),
      'oth' : wx.Colour(150,150,220),
      'io_1': wx.Colour(200,200,200),
      'io_0': wx.Colour(200,200,200),
      'io_z': wx.Colour(128, 128, 128)
    }
  

  def InitUI(self): 

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

    self.m_statusBar1 = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
    self.m_menubar1 = wx.MenuBar( 0 )
    self.m_menu1 = wx.Menu()
    self.m_load = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Load BSDL", wx.EmptyString, wx.ITEM_NORMAL )
    self.m_menu1.Append( self.m_load )

    self.m_exit = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
    self.m_menu1.Append( self.m_exit )

    self.m_menubar1.Append( self.m_menu1, u"File" )

    self.SetMenuBar( self.m_menubar1 )

    #-----------------------
    self.toolbar = self.CreateToolBar()
    self.toolbar.SetToolBitmapSize((16,16))  # sets icon size
 
    # Use wx.ArtProvider for default icons
    open_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
    openTool = self.toolbar.AddSimpleTool(wx.ID_ANY, open_ico, "Save", "Saves the Current Worksheet")
    self.Bind(wx.EVT_MENU, self.loadFile, openTool)
    
    self.toolbar.AddSeparator()
 
    print_ico = wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_TOOLBAR, (16,16))
    printTool = self.toolbar.AddSimpleTool(wx.ID_ANY, print_ico, "Print", "Sends Timesheet to Default Printer")
    # self.Bind(wx.EVT_MENU, self.onPrint, printTool)
 
    # This basically shows the toolbar 
    self.toolbar.Realize()

    # Connect Events
    self.Bind(wx.EVT_MENU, self.loadFile, id= self.m_load.GetId())
    self.Bind(wx.EVT_MENU, self.OnExit, id = self.m_exit.GetId() )

    self.Centre() 
    self.Show(True)
    
  #----------------------------------------------------------------------
  def loadFile(self, event):
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
    try:
      ast = self.parser.parseBSDL(file)

      dev = DUT(ast)
      self.addDev(dev)
      self.m_statusBar1.SetStatusText(file, 1) 
    except tatsu.exceptions.FailedToken:
      self.log(', '.join(["BSDL error parsing ",  file]))  

  def selectDev(self, devid):
    # Select device in main window
    self.m_statusBar1.SetStatusText(', '.join([
      self.devs[devid].name,
      self.devs[devid].package
    ])) 

  def addDev(self, device):
    # Log info
    self.log("Found " + device.name) 
    # Append device to list
    self.devs.append(device)
    # Append device to left panel
    self.leftP.addDev(device)

  def OnExit(self, evt):
    self.Close(True)  

  def log(self, txt):
    self.bottomP.m_textCtrl1.AppendText(txt + '\n')


if __name__ == "__main__":
  bsdl_parser = bsdl_parser.Parser('bsdl.ebnf')
  ex = wx.App() 
  Mywin(None,'JTAG Viewer', parser=bsdl_parser) 
  ex.MainLoop()