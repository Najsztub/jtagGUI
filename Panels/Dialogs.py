import wx
import wx.adv
from Panels import panels
from HWLayer.dut import Pin, Cell

PIN_COLS = {
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

#######################################################################
# Legend dialog
class Legend(panels.Legend):
  #constructor
  def __init__(self,parent):
    
    #initialize parent class
    panels.Legend.__init__(self, parent)

    self.m_panel1.Bind(wx.EVT_PAINT, self.OnPaint) 

    self.width = 24

    self.pin_list = []

    # Populate pin list
    # Not connected
    p_nc = Pin()
    p_nc.name = 'MISSING'
    p_nc.port.name = 'MISSING'
    self.pin_list.append((p_nc, "Not connected"))
    # VCC
    p_vcc = Pin()
    p_vcc.port.name = "VCC"
    self.pin_list.append((p_vcc, "Power pin - Vcc"))
    # GND
    p_gnd = Pin()
    p_gnd.port.name = "GND"
    self.pin_list.append((p_gnd, "Power pin - GND"))
    
    # JTAG
    p_jtag = Pin()
    p_jtag.port.name = "TCK"
    self.pin_list.append((p_jtag, "JTAG port pin"))
    
    # io Z
    p_io_link = Pin()
    p_io_link.port.name = "IN"
    self.pin_list.append((p_io_link, "In pin / linkage - read only"))

    # io 0
    p_io_0 = Pin()
    p_io_0.port.in_cell = Cell(None)
    p_io_0.port.out_cell = Cell(None)
    p_io_0.port.name = "IO1"
    p_io_0.read = '0'
    p_io_0.port.is_set = False
    self.pin_list.append((p_io_0, "I/O pin - read logical 0"))

    # io 1
    p_io_1 = Pin()
    p_io_1.port.in_cell = Cell(None)
    p_io_1.port.out_cell = Cell(None)
    p_io_1.port.name = "IO"
    p_io_1.read = '1'
    p_io_1.port.is_set = False
    self.pin_list.append((p_io_1, "I/O pin - read logical 1"))

    # io 0
    p_iow_0 = Pin()
    p_iow_0.port.in_cell = Cell(None)
    p_iow_0.port.out_cell = Cell(None)
    p_iow_0.port.name = "IO"
    p_iow_0.read = '0'
    p_iow_0.write = '0'
    self.pin_list.append((p_iow_0, "I/O pin - read logical 0, set 0"))

    # io 1
    p_iow_1 = Pin()
    p_iow_1.port.in_cell = Cell(None)
    p_iow_1.port.out_cell = Cell(None)
    p_iow_1.port.name = "IO"
    p_iow_1.read = '1'
    p_iow_1.write = '1'
    self.pin_list.append((p_iow_1, "I/O pin - read logical 1, set 1"))



  def close(self, e):
    self.Destroy()

  def addPin(self, dc, pin_desc, y_coord):
    pin_color = PIN_COLS['oth']

    pin = pin_desc[0]
    
    if pin.port.name[0:3].upper() in ['VCC', 'VDD']: pin_color = PIN_COLS['vcc']
    elif pin.port.name[0:3].upper() in ['GND', 'VSS']:  pin_color = PIN_COLS['gnd']
    elif pin.port.name[0:2].upper() == 'IO':  pin_color = PIN_COLS['io']
    elif pin.port.name.upper() == 'MISSING':  pin_color = PIN_COLS['nc']
    elif pin.port.name[0:3].upper() in ['TDI', 'TDO', 'TCK', 'TMS', 'TRST']:  pin_color = PIN_COLS['jtag']
    dc.SetPen(wx.Pen(wx.Colour(200,200,255), 2)) 
    dc.SetBrush(wx.Brush(pin_color, wx.BRUSHSTYLE_SOLID))

    # Plot pin square
    dc.DrawRectangle(0, y_coord, self.width, self.width) 

    # Draw value to write if pin setting is enabled
    if pin.port.is_set:
      if pin.write == '0': 
        dc.SetBrush(wx.Brush(PIN_COLS['io_0'], wx.BRUSHSTYLE_SOLID))
      elif pin.write == '1': 
        dc.SetBrush(wx.Brush(PIN_COLS['io_1'], wx.BRUSHSTYLE_SOLID))
      dc.DrawPolygon([
        (0, y_coord),
        (0 + self.width, y_coord + self.width),
        (0 + self.width, y_coord)
      ])

    # Draw state if value present, else return
    if pin.read is not None: 
      state_col = PIN_COLS['io_z']
      if pin.read == '0': state_col = PIN_COLS['io_0']
      elif pin.read == '1': state_col = PIN_COLS['io_1']
        
      # Draw circle 
      dc.SetBrush(wx.Brush(state_col, wx.BRUSHSTYLE_SOLID))

      # Include pin type in the picture
      if pin.port.type in ['out']:
        dc.SetPen(wx.Pen(wx.Colour(26, 33, 171), 1, wx.SOLID))
      dc.DrawCircle((0.5 * self.width), (y_coord+0.5 * self.width), (0.3 * self.width))    
      dc.SetPen(wx.Pen(wx.Colour(200,200,255))) 
      dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.TRANSPARENT)) 

    font = wx.Font(self.width, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.DrawText(pin_desc[1], 10 + self.width, y_coord + 0.25*self.width)


  def OnPaint(self, e): 
    dc =  wx.PaintDC(e.GetEventObject())
    dc.Clear() 

    # Loop over pin list
    for i, p in enumerate(self.pin_list):
      self.addPin(dc, p, i * self.width + 0.25 * self.width)

    
    


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

