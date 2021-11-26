import wx

#######################################################################
# Pin popup menu
class PinSetup(wx.Menu):
  def __init__(self, device, port):
    super(PinSetup, self).__init__()
      
    self.device = device
    self.port = port

    high = wx.MenuItem(self, wx.ID_ANY, 'High 1')
    self.Append(high)
    self.Bind(wx.EVT_MENU, self.PinHigh, high)

    low = wx.MenuItem(self, wx.ID_ANY, 'Low 0')
    self.Append(low)
    self.Bind(wx.EVT_MENU, self.PinLow, low)

    reset = wx.MenuItem(self, wx.ID_ANY, 'Reset')
    self.Append(reset)
    self.Bind(wx.EVT_MENU, self.PinReset, reset)

  def PinHigh(self, e):
    self.port.write = '1'

  def PinLow(self, e):
    self.port.write = '0'
    
  def PinReset(self, e):
    self.port.reset()