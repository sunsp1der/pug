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
        self.title = title
        self.Bind(wx.EVT_ACTIVATE, self._evt_on_activate)
        
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
        pass
                
    def refresh(self):
        for child in self.childDict:
            if child.settings['auto_refresh']:
                child.refresh()
                
    def apply(self, event=None):
        for child in self.childDict:
            if child.settings['auto_apply']:
                child.apply_all()
        
    def show_all_attributes(self, event=None):
        """Expand the frame's size so that all attributes are visible"""
        bestSize = self.pugWindow.GetBestSize()
        # give some space for scrollbars
        newSize = (bestSize[0] + WX_SCROLLBAR_FUDGE[0], 
                   bestSize[1] + WX_SCROLLBAR_FUDGE[1] + toolbarFudge)
        # show the whole toolbar
        toolbarWidth = self.GetToolBar().GetSize()[0]
        if newSize[0] < toolbarWidth:
            newSize = (toolbarWidth, newSize[1])
        self.SetClientSize(newSize)
            
    def _evt_passmenu(self, event): 
        # this checking stuff is necessary so that we don't have an infinite
        # recursion with us passing event down then it getting passed up again
        if self.passingMenuEvent:
            self.passingMenuEvent = None
            event.Skip()
        else:
            self.passingMenuEvent = event
            if self.pugWindow:
                self.pugWindow.ProcessEvent(event)
        self.passingMenuEvent = None
                    
    def get_object_list(self):
        """get_object_list() > list of objects displayed in this frame
"""
        return [self.pugWindow.objectRef()]

    def show_object(self, obj):
        """show_object(obj) > reveal the tab containing obj. Not implemented"""
        pass
    
    def on_view_object_deleted(self, window, obj):
        """on_view_object_deleted(window, obj)
        
window: the PugWindow whose object was deleted
obj: the proxy object
Override this callback to affect behavior when an object being viewed in the
pugframe is deleted.
"""
        self.SetTitle(''.join(['Deleted: ', self.GetTitle()]))
        
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
#        wx.GetApp().set_default_pos( self)
        self.setup_window(obj, objectpath, title, name)
        
    def show_all_attributes(self, event=None):
        pass
    
    def setup_tools(self):
        pass
    #TODO:
#        if self.toolBar:
#            self.toolBar.Hide()
#        if self.menuBar:
#            self.menuBar.Hide()
#        if pugWindow.toolBar:
#            toolBar = pugWindow.toolBar
#            self.SetToolBar(toolBar)
#            toolBar.Show()
#            self.toolBar = toolBar
#            toolBar.Realize()
#        if pugWindow.menuBar:
#            menuBar = pugWindow.menuBar
#            self.SetMenuBar(menuBar)
#            menuBar.Show()
#            self.menuBar = menuBar        
