import wx 
import re
import math
import string
from HWLayer.dut import Pin, PinColour

#######################################################################
# Define Right panel class
class RightPanel(wx.Panel):
  """"""
  #----------------------------------------------------------------------
  def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="RightPanel"):
    super(RightPanel, self).__init__(parent, id, pos, size, style, name)
    
    self.dev = None
    self.leftP = None

    self.npins =  None
    self.package = None

    self.EMPTY_PIN = Pin()
    self.EMPTY_PIN.name = 'MISSING'
    self.EMPTY_PIN.port.name = 'MISSING'
  
    # Painting + repainting on resize
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint) 
    # Zooming
    self.Bind(wx.EVT_MOUSEWHEEL, self.OnZoom) 
    # Dragging
    self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
    self.Bind(wx.EVT_MOTION, self.OnMouseMove)

    self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
    
    # Use only logical coordinates
    self.origin = [0, 0]
    self.scale = 1

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
      # Discover number of pins if none in package description
      try:
        npins = max([int(p) for p in self.dev.pins.keys()]) + 1
      except ValueError:
        npins = 0
      npins = max(npins, len(dev.pins))
      self.npins = npins

    # Package specific parsing
    pkg = self.dev.package
    if bool(re.search("BGA", pkg)): 
      self.pkg = 'BGA'
      # Make sure that we include 'holes' in BGA
      pin_names = self.dev.pins.keys()
      pin_gr = [re.match('([A-Za-z]+)([0-9]+)', k).groups() for k in pin_names]
      # Sort rows
      rows = list(set([pt[0] for pt in pin_gr]))
      chars = dict([(k, i) for i,k in enumerate(string.ascii_uppercase)])
      rows = sorted(rows, key = lambda st: sum([pow(26, len(st)-i-1) * (chars[c.upper()]+1) for i,c in enumerate(st)]))
      self.bga_rows = rows
      cols = set([int(pt[1]) for pt in pin_gr])
      self.npins = len(rows) * len(cols)
    else: 
      self.pkg = 'FP'

  def OnSize(self, event):
    event.Skip()
    self.Refresh()

  # TODO: Add selected pin highligth

  # TODO: Add pin menu/panel
  
  def OnPaint(self, e): 
    self.imgx, self.imgy = self.GetClientSize()

    dc =  wx.AutoBufferedPaintDC(self)

    dc.SetDeviceOrigin(int(self.origin[0]), int(self.origin[1]))
    dc.SetUserScale(self.scale, self.scale)

    brush = wx.Brush("white")  
    dc.SetBackground(brush)  
    dc.Clear() 
    
    # Skip if no pins present
    if self.dev is None or self.dev.pins is None: return

    dc.SetPen(wx.Pen(PinColour.DEF.value)) 
    dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.TRANSPARENT)) 
    
    # Get device package and draw appropriate pins
    pkg = self.dev.package
    if self.pkg == 'BGA': self.plotBGA(dc)
    else: self.plotTQFP(dc)

  def plotPin(self, dc, pin, pin_loc, width):
    # Set fill colour depending on Pin name
    pin_color = PinColour.OTH
    port_name = pin.port.name
    if port_name[0:3].upper() in ['VCC', 'VDD']: pin_color = PinColour.VCC
    elif port_name[0:3].upper() in ['GND', 'VSS']:  pin_color = PinColour.GND
    elif port_name[0:2].upper() == 'IO':  pin_color = PinColour.IO
    elif port_name.upper() == 'MISSING':  pin_color = PinColour.NC
    elif port_name[0:3].upper() in ['TDI', 'TDO', 'TCK', 'TMS', 'TRST']:  pin_color = PinColour.JTAG
    dc.SetPen(wx.Pen(PinColour.DEF.value)) 
    dc.SetBrush(wx.Brush(pin_color.value, wx.BRUSHSTYLE_SOLID))

    # Plot pin square
    dc.DrawRectangle(pin_loc[0], pin_loc[1], width, width) 

    # Draw value to write if pin setting is enabled
    if pin.port.is_set:
      if pin.write == '0': 
        dc.SetBrush(wx.Brush(PinColour.IO_0.value, wx.BRUSHSTYLE_SOLID))
      elif pin.write == '1': 
        dc.SetBrush(wx.Brush(PinColour.IO_1.value, wx.BRUSHSTYLE_SOLID))
      dc.DrawPolygon([
        (pin_loc[0], pin_loc[1]),
        (pin_loc[0] + width, pin_loc[1] + width),
        (pin_loc[0] + width, pin_loc[1])
      ])

    # Draw state if value present, else return
    if pin.read is None: return
    state_col = PinColour.IO_Z
    if pin.read == '0': state_col = PinColour.IO_0
    elif pin.read == '1': state_col = PinColour.IO_1
      
    # Draw circle 
    dc.SetBrush(wx.Brush(state_col.value, wx.BRUSHSTYLE_SOLID))

    # Include pin type in the picture
    if pin.port.type in ['out']:
      dc.SetPen(wx.Pen(PinColour.OUT.value, 1, wx.SOLID))
    dc.DrawCircle(int(pin_loc[0] + 0.5 * width), int(pin_loc[1] + 0.5 * width), int(0.3 * width))
  
  def plotTQFP(self, dc):
    side = math.ceil((self.npins) / 4)
    pt_dir = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    pin_width_float = min(self.imgx, self.imgy) * .8 / side
    pin_width_int = int(pin_width_float/2)*2
    border = min(self.imgx, self.imgy) * 0.1
    coord = [math.ceil(border), math.ceil(border)]
    # Set font
    if self.npins < 100:
      font = wx.Font(math.floor(pin_width_float*0.5), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    else:
      font = wx.Font(math.floor(pin_width_float*0.33), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.SetFont(font) 
    # Draw pins in loop 
    for i in range(self.npins):
      # Decide which border it is
      # 1 - bottom
      # 2 - right
      # 3 - top
      # 0 - left
      border_number = math.floor(i / side)
      loc_dir = pt_dir[border_number]
      # Search for item based on on pin nr
      try:
        current_pin = self.dev.pins[str(i+1)]
      except KeyError:
        current_pin = self.EMPTY_PIN
      # Draw rectangles for pins
      # Move pins 1 unit, so they do not overlap in corners
      if (border_number == 1):
        # Bottom
        pin_loc = [int(coord[0] + pin_width_float), int(coord[1])]
        dc.DrawText(str(i+1), int(pin_loc[0]), int(pin_loc[1]+pin_width_float))
      elif (border_number == 2):
        # Right
        pin_loc = [int(coord[0] + pin_width_float), int(coord[1] - pin_width_float)]
        dc.DrawText(str(i+1), int(pin_loc[0] + pin_width_float), int(pin_loc[1]))
      elif (border_number == 3):
        # Top
        pin_loc = [int(coord[0]), int(coord[1] - pin_width_float)]
        dc.DrawText(str(i+1), int(pin_loc[0]), int(pin_loc[1] - pin_width_float))
      else:
        # Left
        pin_loc = [int(coord[0]), int(coord[1])]
        dc.DrawText(str(i+1), int(pin_loc[0] - pin_width_float), int(pin_loc[1]))
      
      # Increment coords
      coord[0] += pin_width_float * loc_dir[0]
      coord[1] += pin_width_float * loc_dir[1]
      
      # Draw pin
      self.plotPin(dc, current_pin, pin_loc, pin_width_int)

  def plotBGA(self, dc):
    side = math.ceil(math.sqrt(self.npins))
    pin_width_float = min(self.imgx, self.imgy) * .8 / side
    pin_width_int = int(pin_width_float/2)*2
    border = min(self.imgx, self.imgy) * 0.1
    # Set font
    font = wx.Font(math.floor(pin_width_float*0.5), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.SetFont(font) 
    for i in range(side):
      # Row pin nr
      dc.DrawText(self.bga_rows[i], int(border - pin_width_float), math.ceil(pin_width_float * i + border))
      for j in range(side):
        # Col pin nr
        if i == 0: dc.DrawText(str(j+1), math.ceil(pin_width_float * j + border), int(border - pin_width_float))
        if self.bga_rows[i] + str(j+1) in self.dev.pins.keys():
          current_pin = self.dev.pins[self.bga_rows[i] + str(j+1)]
        else:
          current_pin = self.EMPTY_PIN
        # Pin coordinates
        pin_loc =[int(border + pin_width_float * j), int(border + pin_width_float* i)]
        # Draw pin
        self.plotPin(dc, current_pin, pin_loc, pin_width_int)

  # Dragging 
  def OnLeftDown(self, e):
    if self.dev is None:
      return
    pt = e.GetPosition()
    self.left_pos = pt
    self.orig_origin = self.origin + []

  def OnMouseMove(self, e):
    if self.dev is None:
      return
    if e.Dragging() and e.LeftIsDown():
      x, y = e.GetPosition()
      delta = (x - self.left_pos[0], y - self.left_pos[1])
      self.origin[0] = self.orig_origin[0] + delta[0] 
      self.origin[1] = self.orig_origin[1] + delta[1] 
      self.Refresh()

  def OnZoom(self, event):
    if self.dev is None:
      return
    """ Scale on mouse scroll """
    # Calculate scaling factor 
    scaling_factor = -event.GetWheelRotation()/event.GetWheelDelta() * 0.1

    pt = event.GetPosition()

    # Change the scaling factor to give max 10 or min 0.1 scale
    if self.scale * (1+scaling_factor) < 0.1:
      scaling_factor = 0.1 / self.scale - 1
    if self.scale * (1+scaling_factor) > 10:
      scaling_factor = 10 / self.scale - 1

    if self.scale > 0.1 and self.scale < 10:

      dx = (pt.x - self.origin[0]) * scaling_factor 
      dy = (pt.y - self.origin[1]) * scaling_factor
      
      self.origin[0] -= dx
      self.origin[1] -= dy
    
    self.scale *= (1+scaling_factor)
    if self.scale < 0.1:
      self.scale = 0.1
    if self.scale > 10:
      self.scale = 10

    self.Refresh()
