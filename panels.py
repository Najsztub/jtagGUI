# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class LeftPanel
###########################################################################

class LeftPanel ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 150,173 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 150,-1 ) )
		self.SetMaxSize( wx.Size( 300,-1 ) )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer3.SetMinSize( wx.Size( -1,5 ) )
		self.m_devLab = wx.StaticText( self, wx.ID_ANY, u"Devices:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_devLab.Wrap( -1 )

		bSizer3.Add( self.m_devLab, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		m_dev_choiceChoices = []
		self.m_dev_choice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_dev_choiceChoices, 0 )
		self.m_dev_choice.SetSelection( 0 )
		bSizer3.Add( self.m_dev_choice, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer2.Add( bSizer3, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		self.m_pinList = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		bSizer4.Add( self.m_pinList, 1, wx.EXPAND|wx.ALL, 5 )


		bSizer2.Add( bSizer4, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer2 )
		self.Layout()

		# Connect Events
		self.m_dev_choice.Bind( wx.EVT_CHOICE, self.selectDev )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def selectDev( self, event ):
		event.Skip()


###########################################################################
## Class BottomPanel
###########################################################################

class BottomPanel ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,100 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( -1,100 ) )
		self.SetMaxSize( wx.Size( -1,300 ) )

		bSizer10 = wx.BoxSizer( wx.VERTICAL )

		self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer10.Add( self.m_textCtrl1, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer10 )
		self.Layout()

	def __del__( self ):
		pass


