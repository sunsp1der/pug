#Boa:Frame:PugFrame
"""PugFrame: The basic pug display frame

This is generally meant to be created by the pug function. You can send the 
object to be viewed as an argument on creation of the frame."""

import wx
import wx.aui

from pug.util import CallbackWeakKeyDictionary
from pug.syswx.pugframe import PugFrame
from pug.syswx.util import get_icon
from pug.syswx.wxconstants import *
from pug.syswx.pugwindow import PugWindow
from pug.syswx.SelectionWindow import SelectionWindow

class PugMDI(wx.aui.AuiMDIParentFrame):
    """A Multi-Document frame that holds Python Universal GUIs
    
PugMDI(self, objInfoList, title, show, parent)
    objInfoList=None: [obj1, obj2, (obj3, kwargs), obj4...] 
        Info about objects to be shown. objInfoList will also accept a single 
        object or list of objects, rather than a list of lists. kwargs is a dict
        of arguments that will be sent to the PugMDIChild frame.
        Common kwargs:
            obj: the object to view
            objectpath: programatic path to object
            title: child frame title
            name: wxFrameNameStr for child frame
        Special object names (instead of objects):
            'selection': opens a selection viewer child
    title="": the frame title. if not provided, set_object will create one
    objectpath="object": relative name e.g. 'mygame.scene.player'
    show=True: call Show on this frame immediately
    parent=None: parent window
"""
    toolBar = None
    menuBar = None
    pugWindow = None
    passingMenuEvent = None
    childNum = 0
    def __init__(self, objInfoList=None, title="", show=True, parent=None, 
                 **kwargs):        
        wx.aui.AuiMDIParentFrame.__init__(self, parent, -1,
                            size=WX_PUGFRAME_DEFAULT_SIZE, title=title,**kwargs) 
        
        sizer = wx.BoxSizer()
        self.SetMinSize(wx.Size(250, 130))
        self.SetIcon(get_icon())
        self.Bind(wx.EVT_ACTIVATE, self._evt_on_activate)
#        menu = wx.Menu()
#        id = wx.NewId()
#        menu.Append(help='Tile windows horizontally', id=id, 
#                    text='Tile horizontal')
#        self.Bind(wx.EVT_MENU, self.tile_horizontal, id=id)
#        id = wx.NewId()
#        menu.Append(help='Tile windows vertically', id=id, 
#                    text='Tile vertical')
#        self.Bind(wx.EVT_MENU, self.tile_vertical, id=id)
        self.SetWindowMenu(None)
        
        if objInfoList and not isinstance(objInfoList, list):
            objInfoList = [objInfoList]
        self.open_obj_info_list( objInfoList)
        self.GetClientWindow().SetSelection(0)
            
        bar = self.CreateStatusBar()        
        bar.Bind(wx.EVT_LEFT_DCLICK, self.show_all_attributes)        
        self.Bind(wx.EVT_MENU, self._evt_passmenu)
        rect = wx.GetApp().get_default_pos( self)
        if rect:
            self.SetPosition((rect[0],rect[1]))
            self.SetSize((rect[2],rect[3]))
        if show:
            self.Show()
            
    def tile_horizontal(self, event=None):
        self.Tile(wx.HORIZONTAL)
    def tile_vertical(self, event=None):
        self.Tile(wx.VERTICAL)

    def open_obj_info_list(self, objInfoList):
        for info in objInfoList:   
            if isinstance(info, list):
                obj = info[0]
                if len(info) > 1:
                    kwargs = info[1]
            else:
                obj = info
            if obj == 'selection':
                child = self.open_selection_child()
            else:
                child = self.open_pug_child(obj, **kwargs)
            
    def open_pug_child(self, obj=None, **kwargs):
        child = PugMDIChild( self, obj, **kwargs)
        return child

    def open_selection_child(self):
        child = self.open_pug_child()
        child.set_pugwindow(SelectionWindow(child))
        return child
            
    def _evt_on_activate(self, event=None):
        if self.pugWindow:
            if event.Active:
                self.refresh()
            else:
                self.apply()
    
    def get_child_list(self):
        childList = []
        nb = self.GetNotebook()
        for page in range(nb.GetPageCount()):
            page = nb.GetPage(page)
            childList.append(page)
        return childList
                
    def refresh(self):
        for child in self.get_child_list():
            child.refresh()
                
    def apply(self, event=None):
        for child in self.get_child_list():
            child.apply()
        
    def show_all_attributes(self, event=None):
        """Pass. AUI doesn't have an interface for getting the best size"""
        pass
    
    def _evt_passmenu(self, event): 
        # this checking stuff is necessary so that we don't have an infinite
        # recursion with us passing event down then it getting passed up again
        if self.passingMenuEvent:
            self.passingMenuEvent = None
            event.Skip()
        else:
            self.passingMenuEvent = event
            pugWindow = getattr(self.GetActiveChild(),'pugWindow',None)
            processed = False
            if pugWindow:
                processed = pugWindow.ProcessEvent(event)
            if not processed:
                event.Skip()
        self.passingMenuEvent = None
                    
    def get_object_list(self):
        "get_object_list() > list of objects displayed in this frame"        
        oblist = []
        for child in self.get_child_list():
            if child.pugWindow.objectRef():
                oblist.append(child.pugWindow.objectRef())
        return oblist

    def show_object(self, obj):
        """show_object(obj) > reveal the tab containing obj. Not implemented"""
        for child in self.get_child_list():
            if child.pugWindow.objectRef() == obj:
                child.Activate()
                
    def on_view_object_deleted(self, window, obj):
        pass
        
class PugMDIChild(wx.aui.AuiMDIChildFrame, PugFrame):
    """PugMDIChild(...): an MDI child derived which operates like a PugFrame
    
(parent, obj=None, objectpath='unknown', title='', name='', **kwargs)
kwargs will be passed to the AuiMDIChildFrame.__init__. PugFrame.__init__ not
called, but PugFrame.setup_window is."""
    def __init__(self, parent, obj=None, objectpath='unknown', title='', 
                 name='', **kwargs):
        wx.aui.AuiMDIChildFrame.__init__(self, parent, -1, '', name=name,
                                         **kwargs)
        self.Bind(wx.EVT_ACTIVATE, self._evt_on_activate)
        self.Bind(wx.EVT_CLOSE, self._evt_on_close)
#        wx.GetApp().set_default_pos( self)
        self.setup_window(obj, objectpath, title, name)
        
    def on_show_object(self, obj=None):
        self.Raise()
        
    def _evt_on_close(self, event):
        if event.CanVeto():
            event.Veto()
        
    def show_all_attributes(self, event=None):
        pass
    
    def setup_tools(self):
        self.SetMenuBar(self.pugWindow.menuBar)
    
    def Raise(self):
        self.GetMDIParentFrame().Show()
        self.GetMDIParentFrame().Iconize(False)
        self.GetMDIParentFrame().Raise()
        self.Iconize(False)
        self.Activate()

