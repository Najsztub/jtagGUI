import wx
from Panels import panels

#######################################################################
# Override BSDL Editor
class BSDLEditor(panels.BSDLEditor):
  #constructor
  def __init__(self,parent):
    panels.BSDLEditor.__init__(self, parent)

  def loadFile(self, event):
    # BSDL file loading dialog
    openFileDialog = wx.FileDialog(self, "Open", "", "", 
                                    "BSDL files (*.bsdl, *.bsd)|*.bsdl;*.bsd|All files (*.*)|*.*", 
                                    wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if openFileDialog.ShowModal() == wx.ID_CANCEL:
      return     # the user changed their mind

    self.me_editor.LoadFile(openFileDialog.GetPath())