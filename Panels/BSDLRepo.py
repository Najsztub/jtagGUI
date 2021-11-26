import wx
import tatsu
from Panels import panels
from HWLayer.dut import DUT

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
    # Compile BSDL parser if not initialized
    if not self.parent.parser.initialized:
      self.parent.log("Initializing BSDL parser. Might take about a minute.")
      self.parent.parser.initialize()
      self.parent.log("DONE Initializing BSDL parser.")
    try:
      self.parent.log("Try parsing BSDL file.")
      ast = self.parent.parser.parseBSDL(pathname)
    except IOError:
      wx.LogError("Cannot open file '%s'." % pathname)
      self.parent.log("Cannot open file '%s'." % pathname)
    except tatsu.exceptions.FailedToken as ex:
      self.parent.log(f"BSDL error parsing {pathname}")
      self.parent.log(ex)
    if ast is not None:
      self.parent.log("Parsing DONE.")
      dev = DUT(ast)
      # Upload info to DB
      ret_data = self.bsdl_repo.addBSDL(dev.getBSDL_IDCODE(), name=dev.name, source=pathname, ast=ast)
      # Add to self.data and table
      self.data.append(ret_data)
      self.m_bsdl_data.AppendItem(ret_data[1:6])
      self.parent.log(f"BSDL definition of {dev.name} successfully added to database.")

    openFileDialog.Destroy()


  def dropBSDL( self, event ):
    row = self.m_bsdl_data.GetSelectedRow()
    if row != wx.NOT_FOUND:
      self.bsdl_repo.delBSDL(self.data[row][0])
    self.m_bsdl_data.DeleteItem(row)
    del self.data[row]

  def exportDb(self, event):
    event.Skip()
