import wx 
import math
import tatsu
import string
import re


class LeftPanel(wx.Panel):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        
        self.SetSizer(sizer)
    
#######################################################################
class RightPanel(wx.Panel):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        txt = wx.TextCtrl(self)

class Mywin(wx.Frame): 

  def __init__(self, parent, title): 
    super(Mywin, self).__init__(parent, title = title,size = (500,500))  
    self.ast = None
    self.InitUI() 

  def InitUI(self): 

    # splitter = wx.SplitterWindow(self)
    # leftP = LeftPanel(splitter)
    # rightP = RightPanel(splitter)

    # # split the window
    # splitter.SplitVertically(leftP, rightP)
    # splitter.SetMinimumPaneSize(20)

    # sizer = wx.BoxSizer(wx.VERTICAL)
    # sizer.Add(splitter, 1, wx.EXPAND)
    # self.SetSizer(sizer)

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
    self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
    self.Bind(wx.EVT_MENU, self.loadFile, id= self.m_load.GetId())
    self.Bind(wx.EVT_MENU, self.OnExit, id = self.m_exit.GetId() )
    self.Bind(wx.EVT_PAINT, self.OnPaint) 
    self.Bind(wx.EVT_SIZE, self.OnSize)

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
      with open(pathname, 'r') as file:
        self.loadBSDL(file)
    except IOError:
      wx.LogError("Cannot open file '%s'." % pathname)
    openFileDialog.Destroy()

  def loadBSDL(self, file):
    try:
      self.ast = bsdl_model.parse(file.read(), "bsdl_description", semantics=BsdlSemantics(), parseinfo=False, ignorecase=True)

      pins = self.ast['device_package_pin_mappings'][0]['pin_map']
      self.pins = dict([(pn, p['port_name']) for p in pins for pn in p['pin_list']])
      self.m_statusBar1.SetStatusText(', '.join([
        self.ast["component_name"],
        self.ast["generic_parameter"]["default_device_package_type"]
      ])) 
      self.Refresh()
    except tatsu.exceptions.FailedToken:
      self.m_statusBar1.SetStatusText(', '.join(["BSDL error parsing ",  file.name]))

  def OnSize(self, event):
    event.Skip()
    self.Refresh()

  def OnPaint(self, e): 
    self.imgx, self.imgy = self.GetClientSize()
    dc =  wx.AutoBufferedPaintDC(self)
    brush = wx.Brush("white")  
    dc.SetBackground(brush)  
    dc.Clear() 
    if self.ast is None: return

    pen = wx.Pen(wx.Colour(0,0,255)) 
    dc.SetPen(pen) 
    dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.TRANSPARENT)) 
    pkg = self.ast["generic_parameter"]["default_device_package_type"]
    if bool(re.search("BGA", pkg)): self.plotBGA(dc)
    else: self.plotTQFP(dc)
    
  def plotTQFP(self, dc):
    npins = len(self.pins)
    side = math.ceil(npins / 4)
    pt_dir = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    rec_b = min(self.imgx, self.imgy) * .8 / side
    coord = [60, 30]
    for i in range(npins):
      loc_dir = pt_dir[math.floor(i / side)]
      it = self.pins[str(i+1)]
      if it == 'VCC':  dc.SetBrush(wx.Brush(wx.Colour(255,0,0), wx.BRUSHSTYLE_SOLID)) 
      elif it == 'GND':  dc.SetBrush(wx.Brush(wx.Colour(10,10,10), wx.BRUSHSTYLE_SOLID)) 
      elif it[0:2] == 'IO':  dc.SetBrush(wx.Brush(wx.Colour(100,1000,255), wx.BRUSHSTYLE_SOLID)) 
      else : dc.SetBrush(wx.Brush(wx.Colour(100,200,100), wx.SOLID)) 
      if ( math.floor(i / side) == 1):
        dc.DrawRectangle(math.floor(coord[0]), math.floor(coord[1] +  rec_b), math.floor(rec_b), math.floor(rec_b)) 
      elif (math.floor(i / side) == 2):
        dc.DrawRectangle(math.floor(coord[0] - rec_b), math.floor(coord[1] +  rec_b), math.floor(rec_b), math.floor(rec_b)) 
      elif (math.floor(i / side) == 3):
        dc.DrawRectangle(math.floor(coord[0] - rec_b), math.floor(coord[1]), math.floor(rec_b), math.floor(rec_b)) 
      else:
        dc.DrawRectangle(math.floor(coord[0]), math.floor(coord[1]), math.floor(rec_b), math.floor(rec_b)) 
      coord[0] += rec_b * loc_dir[0]
      coord[1] += rec_b * loc_dir[1]



  def plotBGA(self, dc):
    chars = [char for char in string.ascii_uppercase if char not in 'IOQS']
    rec_b = min(self.imgx, self.imgy) * .8 / 16
    for i in range(16):
      for j in range(16):
        it = self.pins[chars[i] + str(j+1)]
        if it == 'VCC':  dc.SetBrush(wx.Brush(wx.Colour(255,0,0), wx.BRUSHSTYLE_SOLID)) 
        elif it == 'GND':  dc.SetBrush(wx.Brush(wx.Colour(10,10,10), wx.BRUSHSTYLE_SOLID)) 
        elif it[0:2] == 'IO':  dc.SetBrush(wx.Brush(wx.Colour(100,1000,255), wx.BRUSHSTYLE_SOLID)) 
        else : dc.SetBrush(wx.Brush(wx.Colour(100,200,100), wx.SOLID)) 
        dc.DrawRectangle(20 + math.ceil(rec_b * i), 30 + math.floor(rec_b* j), math.floor(rec_b), math.floor(rec_b)) 

  def OnExit(self, evt):
    self.Close(True)  


if __name__ == "__main__":
  grammar = open('bsdl.ebnf').read()
  # tatsu.to_python_sourcecode(grammar)
  bsdl_model = tatsu.compile(grammar, ignorecase=True)

  class BsdlSemantics:
    def map_string(self, ast):
      ast = bsdl_model.parse(''.join(ast), "port_map")
      return ast

    def grouped_port_identification(self, ast):
      ast = bsdl_model.parse(''.join(ast), "group_table")
      return ast
    

  ex = wx.App() 
  Mywin(None,'Drawing demo') 
  ex.MainLoop()