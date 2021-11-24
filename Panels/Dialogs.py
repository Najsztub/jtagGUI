import wx
import wx.adv
from Panels import panels


#######################################################################
# Legend dialog
class Legend(panels.Legend):
  #constructor
  def __init__(self,parent):
    
    #initialize parent class
    panels.Legend.__init__(self, parent)

  def close(self, e):
    self.Destroy()

#######################################################################
# About dialog
class About:
  description = """JTAG GUI is a wrapper for UrJTAG designed to
display and set pin states on ICs using the JTAG TAP protocol.
It alows to import and parse BSDL files using TaTsu package,
saving them in local SQLite database."""

  licence = """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""

  info = wx.adv.AboutDialogInfo()

  info.SetName('JTAG GUI')
  info.SetVersion('0.1')
  info.SetDescription(description)
  info.SetCopyright('(C) 2020-2021 Mateusz Najsztub')
  info.SetWebSite('https://github.com/Najsztub/jtagGUI')
  info.SetLicence(licence)

