# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"JTAG GUI", pos = wx.DefaultPosition, size = wx.Size( 640,480 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_statusBar1 = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menu1 = wx.Menu()
        self.m_load = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Load BSDL", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_load.SetBitmap( wx.NullBitmap )
        self.m_menu1.Append( self.m_load )

        self.m_exit = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.m_exit )

        self.m_menubar1.Append( self.m_menu1, u"File" )

        self.m_menu2 = wx.Menu()
        self.m_menubar1.Append( self.m_menu2, u"Chain" )

        self.m_menu3 = wx.Menu()
        self.m_bsld_repo = wx.MenuItem( self.m_menu3, wx.ID_ANY, u"BSDL repository", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu3.Append( self.m_bsld_repo )

        self.m_menubar1.Append( self.m_menu3, u"Tools" )

        self.SetMenuBar( self.m_menubar1 )

        self.m_toolbar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        self.m_t_open = self.m_toolbar1.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Open BSDL file", wx.EmptyString, None )

        self.m_toolbar1.AddSeparator()

        self.m_chain_start = self.m_toolbar1.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_PLUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Start JTAG chin", wx.EmptyString, None )

        self.m_chain_stop = self.m_toolbar1.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_CLOSE,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Stop JTAG chain", wx.EmptyString, None )

        m_cableChoices = [ u"Select device", u"usbblaster" ]
        self.m_cable = wx.Choice( self.m_toolbar1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_cableChoices, 0 )
        self.m_cable.SetSelection( 0 )
        self.m_toolbar1.AddControl( self.m_cable )
        self.m_scan_tap = wx.Button( self.m_toolbar1, wx.ID_ANY, u"Scan", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_scan_tap.Enable( False )

        self.m_toolbar1.AddControl( self.m_scan_tap )
        self.m_toolbar1.Realize()


        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_MENU, self.loadFile, id = self.m_load.GetId() )
        self.Bind( wx.EVT_MENU, self.OnExit, id = self.m_exit.GetId() )
        self.Bind( wx.EVT_MENU, self.editBSDLrepo, id = self.m_bsld_repo.GetId() )
        self.Bind( wx.EVT_TOOL, self.loadFile, id = self.m_t_open.GetId() )
        self.Bind( wx.EVT_TOOL, self.attachChain, id = self.m_chain_start.GetId() )
        self.Bind( wx.EVT_TOOL, self.dropChain, id = self.m_chain_stop.GetId() )
        self.m_scan_tap.Bind( wx.EVT_BUTTON, self.scanTAP )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def loadFile( self, event ):
        event.Skip()

    def OnExit( self, event ):
        event.Skip()

    def editBSDLrepo( self, event ):
        event.Skip()


    def attachChain( self, event ):
        event.Skip()

    def dropChain( self, event ):
        event.Skip()

    def scanTAP( self, event ):
        event.Skip()


###########################################################################
## Class LeftPanel
###########################################################################

class LeftPanel ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 285,603 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
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

        self.m_treeListCtrl1 = wx.dataview.TreeListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.TL_DEFAULT_STYLE )
        self.m_treeListCtrl1.AppendColumn( u"Properties", wx.COL_WIDTH_DEFAULT, wx.ALIGN_LEFT, wx.COL_RESIZABLE|wx.COL_SORTABLE )
        self.m_treeListCtrl1.AppendColumn( u"Values", wx.COL_WIDTH_DEFAULT, wx.ALIGN_LEFT, wx.COL_RESIZABLE )

        bSizer4.Add( self.m_treeListCtrl1, 1, wx.EXPAND |wx.ALL, 5 )

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


###########################################################################
## Class BSDLRepo
###########################################################################

class BSDLRepo ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"BSDL definitions repository", pos = wx.DefaultPosition, size = wx.Size( 794,412 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        self.m_toolBar2 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
        self.m_bsdl_add = self.m_toolBar2.AddLabelTool( wx.ID_ANY, u"Add BSDL definition", wx.ArtProvider.GetBitmap( wx.ART_PLUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

        self.m_bsdl_drop = self.m_toolBar2.AddLabelTool( wx.ID_ANY, u"Drop BSDL definition", wx.ArtProvider.GetBitmap( wx.ART_MINUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

        self.m_toolBar2.Realize()

        bSizer6.Add( self.m_toolBar2, 0, wx.EXPAND, 5 )

        self.m_bsdl_data = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_MULTIPLE )
        self.m_bsdl_name = self.m_bsdl_data.AppendTextColumn( u"Name", wx.DATAVIEW_CELL_ACTIVATABLE, 150, wx.ALIGN_LEFT, wx.DATAVIEW_COL_RESIZABLE|wx.DATAVIEW_COL_SORTABLE )
        self.m_bsdl_date_add = self.m_bsdl_data.AppendTextColumn( u"Date added", wx.DATAVIEW_CELL_INERT, 150, wx.ALIGN_LEFT, wx.DATAVIEW_COL_RESIZABLE|wx.DATAVIEW_COL_SORTABLE )
        self.m_bsdl_idcode = self.m_bsdl_data.AppendTextColumn( u"IDCODE", wx.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT, wx.DATAVIEW_COL_RESIZABLE )
        self.m_bsdl_source = self.m_bsdl_data.AppendTextColumn( u"Source", wx.DATAVIEW_CELL_INERT, -1, wx.ALIGN_LEFT, wx.DATAVIEW_COL_RESIZABLE )
        self.m_bsdl_has_ast = self.m_bsdl_data.AppendToggleColumn( u"AST", wx.DATAVIEW_CELL_INERT, 50, wx.ALIGN_LEFT, 0 )
        bSizer6.Add( self.m_bsdl_data, 1, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer6 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_TOOL, self.addBSDL, id = self.m_bsdl_add.GetId() )
        self.Bind( wx.EVT_TOOL, self.dropBSDL, id = self.m_bsdl_drop.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def addBSDL( self, event ):
        event.Skip()

    def dropBSDL( self, event ):
        event.Skip()


