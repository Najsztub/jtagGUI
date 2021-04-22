import wx 
import re
import math
import string
from HWLayer.dut import Pin

#######################################################################
# Define Right panel class
class RightPanel(wx.Panel):
  """"""
  #----------------------------------------------------------------------
  def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="RightPanel"):
    super(RightPanel, self).__init__(parent, id, pos, size, style, name)
    
    self.dev = None
    self.leftP = None
    self.mainW = None

    self.npins =  None
    self.package = None

    self.EMPTY_PIN = Pin()
    self.EMPTY_PIN.name = 'MISSING'
    self.EMPTY_PIN.port.type= 'NC'
  
    self.Bind(wx.EVT_SIZE, self.OnSize)
    self.Bind(wx.EVT_PAINT, self.OnPaint) 
    self.Bind(wx.EVT_MOUSEWHEEL, self.OnZoom) 
    self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

    self.origin = [0, 0]
    self.logical_origin = [0,0]
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
      self.npins = len(dev.pins)

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
  
  def OnZoom(self, event):
    """ Scale on mouse scrool """
    scale = -event.GetWheelRotation()/event.GetWheelDelta()
    pt = event.GetPosition()

    if self.scale > 0.1 and self.scale < 10:
      dx = (self.logical_origin[0] - pt.x) * scale 
      dy = (self.logical_origin[1] - pt.y) * scale 
      
      self.origin[0] += dx /self.scale
      self.origin[1] += dy /self.scale

      self.origin[0] = round(self.origin[0])
      self.origin[1] = round(self.origin[1])
    
    self.scale += scale
    if self.scale < 0.1:
      self.scale = 0.1
    if self.scale > 10:
      self.scale = 10

    self.Refresh()

  def OnPaint(self, e): 
    self.imgx, self.imgy = self.GetClientSize()

    dc =  wx.AutoBufferedPaintDC(self)
    dc.SetUserScale(self.scale, self.scale)
    dc.SetDeviceOrigin(self.origin[0], self.origin[1])

    self.logical_origin = dc.LogicalToDevice(0,0)

    brush = wx.Brush("white")  
    dc.SetBackground(brush)  
    dc.Clear() 
    
    # Skip if no pins present
    if self.dev is None or self.dev.pins is None: return

    dc.SetPen(wx.Pen(wx.Colour(200,200,255))) 
    dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.TRANSPARENT)) 
    
    # Get device package and draw appropriate pins
    pkg = self.dev.package
    if self.pkg == 'BGA': self.plotBGA(dc)
    else: self.plotTQFP(dc)

  def plotPin(self, dc, pin, pt, width):
    # Set fill colour depending on Pin name
    pin_color = self.mainW.PIN_COLS['oth']
    port_name = pin.port.name
    if port_name[0:3].upper() == 'VCC': pin_color = self.mainW.PIN_COLS['vcc']
    elif port_name[0:3].upper() in ['GND', 'VSS']:  pin_color = self.mainW.PIN_COLS['gnd']
    elif port_name[0:2].upper() == 'IO':  pin_color = self.mainW.PIN_COLS['io']
    elif port_name.upper() == 'MISSING':  pin_color = self.mainW.PIN_COLS['nc']
    elif port_name[0:3].upper() in ['TDI', 'TDO', 'TCK', 'TMS', 'TRST']:  pin_color = self.mainW.PIN_COLS['jtag']
    dc.SetPen(wx.Pen(wx.Colour(200,200,255))) 
    dc.SetBrush(wx.Brush(pin_color, wx.BRUSHSTYLE_SOLID))

    # Plot pin square
    dc.DrawRectangle(pt[0], pt[1], width, width) 

    # Draw state
    if pin.read is not None:
      state_col = self.mainW.PIN_COLS['io_z']
      if pin.read == '0': state_col = self.mainW.PIN_COLS['io_0']
      elif pin.read == '1': state_col = self.mainW.PIN_COLS['io_1']
      
      # Draw circle 
      dc.SetBrush(wx.Brush(state_col, wx.BRUSHSTYLE_SOLID))

      # Include pin type in the picture
      if pin.port.type in ['out']:
        dc.SetPen(wx.Pen(wx.Colour(26, 33, 171), 1, wx.SOLID))
      dc.DrawCircle((pt[0] + 0.5 * width), (pt[1] + 0.5 * width), (0.3 * width))
  
  def plotTQFP(self, dc):
    side = math.ceil((self.npins) / 4)
    pt_dir = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    rec_b = min(self.imgx, self.imgy) * .8 / side
    pin_w = int(rec_b/2)*2
    border = min(self.imgx, self.imgy) * 0.1
    coord = [math.ceil(border), math.ceil(border)]
    # Set font
    if self.npins < 100:
      font = wx.Font(math.floor(rec_b*0.5), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    else:
      font = wx.Font(math.floor(rec_b*0.33), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.SetFont(font) 
    for i in range(self.npins):
      loc_dir = pt_dir[math.floor(i / side)]
      # Search for item based on on pin nr
      try:
        it = self.dev.pins[str(i+1)]
      except KeyError:
        it = self.EMPTY_PIN
      # Draw rectangles for pins
      # Move pins 1 unit, so they do not overlap in corners
      if ( math.floor(i / side) == 2):
        # Right
        pt = [(coord[0] + rec_b), (coord[1] - rec_b)]
        dc.DrawText(str(i+1), pt[0] + rec_b, (pt[1]))
      elif (math.floor(i / side) == 1):
        # Bottom
        pt = [(coord[0] + rec_b), (coord[1])]
        dc.DrawText(str(i+1), pt[0], (pt[1]+rec_b))
      elif (math.floor(i / side) == 3):
        # Top
        pt = [(coord[0]), (coord[1] - rec_b)]
        dc.DrawText(str(i+1), pt[0], (pt[1]- rec_b))
      else:
        # Left
        pt = [(coord[0]), (coord[1])]
        dc.DrawText(str(i+1), pt[0] - rec_b, (pt[1]))
      
      # Increment coords
      coord[0] += rec_b * loc_dir[0]
      coord[1] += rec_b * loc_dir[1]
      
      # Draw pin
      self.plotPin(dc, it, pt, pin_w)

  def plotBGA(self, dc):
    side = math.ceil(math.sqrt(self.npins))
    rec_b = min(self.imgx, self.imgy) * .8 / side
    pin_w = int(rec_b/2)*2
    border = min(self.imgx, self.imgy) * 0.1
    # Set font
    font = wx.Font(math.floor(rec_b*0.5), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) 
    dc.SetFont(font) 
    for i in range(side):
      # Row pin nr
      dc.DrawText(self.bga_rows[i], int(border - rec_b), math.ceil(rec_b * i + border))
      for j in range(side):
        # Col pin nr
        if i == 0: dc.DrawText(str(j+1), math.ceil(rec_b * j + border), int(border - rec_b))
        try:
          it = self.dev.pins[self.bga_rows[i] + str(j+1)]
        except KeyError:
          it = self.EMPTY_PIN
        # Draw pin
        pt =[(border + rec_b * j),(border + rec_b* i)]

        # Draw pin
        self.plotPin(dc, it, pt, pin_w)