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
import wx.aui

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
        self.m_mch_sir = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Shift IR"+ u"\t" + u"CTRL+i", u"Shift IR", wx.ITEM_NORMAL )
        self.m_menu2.Append( self.m_mch_sir )

        self.m_mch_sdr = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Shift DR"+ u"\t" + u"CTRL+d", u"Shift DR", wx.ITEM_NORMAL )
        self.m_menu2.Append( self.m_mch_sdr )

        self.m_menu2.AppendSeparator()

        self.m_mauto = wx.Menu()
        self.m_mauto_1 = wx.MenuItem( self.m_mauto, wx.ID_ANY, u"1 s", wx.EmptyString, wx.ITEM_CHECK )
        self.m_mauto.Append( self.m_mauto_1 )

        self.m_mauto_2 = wx.MenuItem( self.m_mauto, wx.ID_ANY, u"1/2 s", wx.EmptyString, wx.ITEM_CHECK )
        self.m_mauto.Append( self.m_mauto_2 )

        self.m_mauto_4 = wx.MenuItem( self.m_mauto, wx.ID_ANY, u"1/4 s", wx.EmptyString, wx.ITEM_CHECK )
        self.m_mauto.Append( self.m_mauto_4 )

        self.m_mauto_8 = wx.MenuItem( self.m_mauto, wx.ID_ANY, u"1/8 s", wx.EmptyString, wx.ITEM_CHECK )
        self.m_mauto.Append( self.m_mauto_8 )

        self.m_mauto.AppendSeparator()

        self.m_mauto_off = wx.MenuItem( self.m_mauto, wx.ID_ANY, u"Off", wx.EmptyString, wx.ITEM_CHECK )
        self.m_mauto.Append( self.m_mauto_off )
        self.m_mauto_off.Check( True )

        self.m_menu2.AppendSubMenu( self.m_mauto, u"DR auto update" )

        self.m_menubar1.Append( self.m_menu2, u"Chain" )

        self.m_menu3 = wx.Menu()
        self.m_bsld_repo = wx.MenuItem( self.m_menu3, wx.ID_ANY, u"BSDL repository", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu3.Append( self.m_bsld_repo )

        self.m_menubar1.Append( self.m_menu3, u"Tools" )

        self.SetMenuBar( self.m_menubar1 )

        self.m_toolbar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        self.m_t_open = self.m_toolbar1.AddTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Open BSDL file", wx.EmptyString, None )

        self.m_toolbar1.AddSeparator()

        self.m_chain_stop = self.m_toolbar1.AddTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_CLOSE,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Stop JTAG chain", wx.EmptyString, None )

        m_cableChoices = [ u"Select device", u"usbblaster" ]
        self.m_cable = wx.Choice( self.m_toolbar1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_cableChoices, 0 )
        self.m_cable.SetSelection( 0 )
        self.m_toolbar1.AddControl( self.m_cable )
        self.m_chain_start = self.m_toolbar1.AddTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_PLUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Start JTAG chin", wx.EmptyString, None )

        self.m_scan_tap = wx.Button( self.m_toolbar1, wx.ID_ANY, u"Scan", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_scan_tap.Enable( False )

        self.m_toolbar1.AddControl( self.m_scan_tap )
        self.m_toolbar1.Realize()


        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_MENU, self.loadFile, id = self.m_load.GetId() )
        self.Bind( wx.EVT_MENU, self.OnExit, id = self.m_exit.GetId() )
        self.Bind( wx.EVT_MENU, self.shiftIR, id = self.m_mch_sir.GetId() )
        self.Bind( wx.EVT_MENU, self.shiftDR, id = self.m_mch_sdr.GetId() )
        self.Bind( wx.EVT_MENU, self.dr_timer_chng, id = self.m_mauto_1.GetId() )
        self.Bind( wx.EVT_MENU, self.dr_timer_chng, id = self.m_mauto_2.GetId() )
        self.Bind( wx.EVT_MENU, self.dr_timer_chng, id = self.m_mauto_4.GetId() )
        self.Bind( wx.EVT_MENU, self.dr_timer_chng, id = self.m_mauto_8.GetId() )
        self.Bind( wx.EVT_MENU, self.dr_timer_chng, id = self.m_mauto_off.GetId() )
        self.Bind( wx.EVT_MENU, self.editBSDLrepo, id = self.m_bsld_repo.GetId() )
        self.Bind( wx.EVT_TOOL, self.loadFile, id = self.m_t_open.GetId() )
        self.Bind( wx.EVT_TOOL, self.dropChain, id = self.m_chain_stop.GetId() )
        self.Bind( wx.EVT_TOOL, self.attachChain, id = self.m_chain_start.GetId() )
        self.m_scan_tap.Bind( wx.EVT_BUTTON, self.scanTAP )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def loadFile( self, event ):
        event.Skip()

    def OnExit( self, event ):
        event.Skip()

    def shiftIR( self, event ):
        event.Skip()

    def shiftDR( self, event ):
        event.Skip()

    def dr_timer_chng( self, event ):
        event.Skip()





    def editBSDLrepo( self, event ):
        event.Skip()


    def dropChain( self, event ):
        event.Skip()

    def attachChain( self, event ):
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

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_bt_shift_ir = wx.Button( self, wx.ID_ANY, u"Shift IR", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_bt_shift_ir, 0, wx.ALL, 5 )

        self.m_bt_get_dr = wx.Button( self, wx.ID_ANY, u"Shift DR", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_bt_get_dr, 0, wx.ALL, 5 )


        bSizer2.Add( bSizer6, 0, 0, 5 )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.m_chain = wx.dataview.TreeListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.TL_DEFAULT_STYLE )
        self.m_chain.SetMinSize( wx.Size( -1,80 ) )

        self.m_chain.AppendColumn( u"Properties", wx.COL_WIDTH_AUTOSIZE, wx.ALIGN_LEFT, wx.COL_RESIZABLE|wx.COL_SORTABLE )
        self.m_chain.AppendColumn( u"*", wx.COL_WIDTH_AUTOSIZE, wx.ALIGN_LEFT, 0 )
        self.m_chain.AppendColumn( u"Values", wx.COL_WIDTH_AUTOSIZE, wx.ALIGN_LEFT, wx.COL_RESIZABLE )

        bSizer4.Add( self.m_chain, 1, wx.EXPAND |wx.ALL, 5 )

        self.m_pinList = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
        bSizer4.Add( self.m_pinList, 1, wx.EXPAND|wx.ALL, 5 )


        bSizer2.Add( bSizer4, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer2 )
        self.Layout()

        # Connect Events
        self.m_bt_shift_ir.Bind( wx.EVT_BUTTON, self.shiftIR )
        self.m_bt_get_dr.Bind( wx.EVT_BUTTON, self.shiftDR )
        self.m_chain.Bind( wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.instSet )
        self.m_chain.Bind( wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.propCheck )
        self.m_pinList.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.pinListRight )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def shiftIR( self, event ):
        event.Skip()

    def shiftDR( self, event ):
        event.Skip()

    def instSet( self, event ):
        event.Skip()

    def propCheck( self, event ):
        event.Skip()

    def pinListRight( self, event ):
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
        self.m_bsdl_add = self.m_toolBar2.AddTool( wx.ID_ANY, u"Add BSDL definition", wx.ArtProvider.GetBitmap( wx.ART_PLUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add BSDL file", u"Add BSDL file to repository", None )

        self.m_bsdl_drop = self.m_toolBar2.AddTool( wx.ID_ANY, u"Drop BSDL definition", wx.ArtProvider.GetBitmap( wx.ART_MINUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Delete BSDL file", u"Delete BSDL file from repository", None )

        self.m_toolBar2.AddSeparator()

        self.m_backup = self.m_toolBar2.AddTool( wx.ID_ANY, u"tool", wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Export backup", u"Export backup (SQLite)", None )

        self.m_toolBar2.Realize()

        bSizer6.Add( self.m_toolBar2, 0, wx.EXPAND, 5 )

        self.m_bsdl_data = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_MULTIPLE )
        self.m_bsdl_name = self.m_bsdl_data.AppendTextColumn( u"Name", wx.dataview.DATAVIEW_CELL_ACTIVATABLE, 150, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE|wx.dataview.DATAVIEW_COL_SORTABLE )
        self.m_bsdl_date_add = self.m_bsdl_data.AppendTextColumn( u"Date added", wx.dataview.DATAVIEW_CELL_INERT, 150, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE|wx.dataview.DATAVIEW_COL_SORTABLE )
        self.m_bsdl_idcode = self.m_bsdl_data.AppendTextColumn( u"IDCODE", wx.dataview.DATAVIEW_CELL_INERT, 150, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_bsdl_source = self.m_bsdl_data.AppendTextColumn( u"Source", wx.dataview.DATAVIEW_CELL_INERT, 250, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_bsdl_has_ast = self.m_bsdl_data.AppendToggleColumn( u"AST", wx.dataview.DATAVIEW_CELL_INERT, 50, wx.ALIGN_LEFT, 0 )
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


###########################################################################
## Class DefineDevice
###########################################################################

class DefineDevice ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Define new Device", pos = wx.DefaultPosition, size = wx.Size( 637,473 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )

        self.m_toolBar3 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
        self.m_staticText2 = wx.StaticText( self.m_toolBar3, wx.ID_ANY, u"Registers", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )

        self.m_toolBar3.AddControl( self.m_staticText2 )
        self.m_r_add = self.m_toolBar3.AddTool( wx.ID_ANY, u"tool", wx.ArtProvider.GetBitmap( wx.ART_PLUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add new register", wx.EmptyString, None )

        self.m_r_del = self.m_toolBar3.AddTool( wx.ID_ANY, u"tool", wx.ArtProvider.GetBitmap( wx.ART_MINUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Remove register", wx.EmptyString, None )

        self.m_toolBar3.Realize()

        bSizer10.Add( self.m_toolBar3, 0, wx.EXPAND|wx.LEFT, 5 )

        self.m_reg_list = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_HORIZ_RULES )
        self.m_r_name = self.m_reg_list.AppendTextColumn( u"Register name", wx.dataview.DATAVIEW_CELL_EDITABLE, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_r_len = self.m_reg_list.AppendTextColumn( u"Register length", wx.dataview.DATAVIEW_CELL_EDITABLE, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        bSizer10.Add( self.m_reg_list, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer8.Add( bSizer10, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.VERTICAL )

        self.m_toolBar4 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
        self.m_staticText4 = wx.StaticText( self.m_toolBar4, wx.ID_ANY, u"Instructions", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )

        self.m_toolBar4.AddControl( self.m_staticText4 )
        self.m_i_add = self.m_toolBar4.AddTool( wx.ID_ANY, u"tool", wx.ArtProvider.GetBitmap( wx.ART_PLUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

        self.m_i_del = self.m_toolBar4.AddTool( wx.ID_ANY, u"tool", wx.ArtProvider.GetBitmap( wx.ART_MINUS,  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

        self.m_toolBar4.Realize()

        bSizer11.Add( self.m_toolBar4, 0, wx.EXPAND|wx.LEFT, 5 )

        self.m_inst_list = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_i_name = self.m_inst_list.AppendTextColumn( u"Instruction name", wx.dataview.DATAVIEW_CELL_EDITABLE, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_i_opcode = self.m_inst_list.AppendTextColumn( u"Opcode", wx.dataview.DATAVIEW_CELL_EDITABLE, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        self.m_i_reg = self.m_inst_list.AppendTextColumn( u"Reg", wx.dataview.DATAVIEW_CELL_EDITABLE, -1, wx.ALIGN_LEFT, wx.dataview.DATAVIEW_COL_RESIZABLE )
        bSizer11.Add( self.m_inst_list, 1, wx.ALL|wx.EXPAND, 5 )


        bSizer8.Add( bSizer11, 1, wx.EXPAND, 5 )


        bSizer7.Add( bSizer8, 1, wx.EXPAND, 5 )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"You need to provide at least IR length", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )

        bSizer9.Add( self.m_staticText5, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_dev_bsdl = wx.Button( self, wx.ID_ANY, u"Import BSDL", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.m_dev_bsdl, 0, wx.ALL, 5 )

        self.m_dev_ok = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.m_dev_ok, 0, wx.ALL, 5 )


        bSizer7.Add( bSizer9, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer7 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_TOOL, self.regAdd, id = self.m_r_add.GetId() )
        self.Bind( wx.EVT_TOOL, self.regDrop, id = self.m_r_del.GetId() )
        self.m_reg_list.Bind( wx.dataview.EVT_DATAVIEW_ITEM_VALUE_CHANGED, self.regChange, id = wx.ID_ANY )
        self.Bind( wx.EVT_TOOL, self.instAdd, id = self.m_i_add.GetId() )
        self.Bind( wx.EVT_TOOL, self.instDrop, id = self.m_i_del.GetId() )
        self.m_inst_list.Bind( wx.dataview.EVT_DATAVIEW_ITEM_VALUE_CHANGED, self.instChange, id = wx.ID_ANY )
        self.m_dev_bsdl.Bind( wx.EVT_BUTTON, self.importBSDL )
        self.m_dev_ok.Bind( wx.EVT_BUTTON, self.defDone )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def regAdd( self, event ):
        event.Skip()

    def regDrop( self, event ):
        event.Skip()

    def regChange( self, event ):
        event.Skip()

    def instAdd( self, event ):
        event.Skip()

    def instDrop( self, event ):
        event.Skip()

    def instChange( self, event ):
        event.Skip()

    def importBSDL( self, event ):
        event.Skip()

    def defDone( self, event ):
        event.Skip()


###########################################################################
## Class BSDLEditor
###########################################################################

class BSDLEditor ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"BSDL File Editor", pos = wx.DefaultPosition, size = wx.Size( 858,680 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.m_mgr = wx.aui.AuiManager()
        self.m_mgr.SetManagedWindow( self )
        self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.m_menubar2 = wx.MenuBar( 0 )
        self.SetMenuBar( self.m_menubar2 )

        self.m_statusBar2 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_auinotebook2 = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
        self.m_mgr.AddPane( self.m_auinotebook2, wx.aui.AuiPaneInfo() .Left() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ) )


        self.m_listbook1 = wx.Listbook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT )
        self.m_mgr.AddPane( self.m_listbook1, wx.aui.AuiPaneInfo() .Left() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ) )


        self.m_auinotebook3 = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
        self.m_mgr.AddPane( self.m_auinotebook3, wx.aui.AuiPaneInfo() .Left() .PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ) )



        self.m_mgr.Update()
        self.Centre( wx.BOTH )

    def __del__( self ):
        self.m_mgr.UnInit()



