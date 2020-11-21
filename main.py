import wx 
import wx.lib.mixins.listctrl as listmix

from Panels import MainWindow
from HWLayer import bsdl_parser

import sys

if __name__ == "__main__":
  print(sys.argv)
  bsdl_parser = bsdl_parser.Parser('bsdl/bsdl.ebnf')
  ex = wx.App() 
  MainWindow.Mywin(None,'JTAG Viewer', parser=bsdl_parser) 
  ex.MainLoop()