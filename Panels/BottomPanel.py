from Panels import panels

#######################################################################
# Override wxFormBuilder BottomPanel class
class BottomPanel(panels.BottomPanel):
  #constructor
  def __init__(self,parent):
    #initialize parent class
    panels.BottomPanel.__init__(self, parent)

