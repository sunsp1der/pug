#Boa:Frame:PugFrame
"""PugFrame: The basic pug display frame

This is generally meant to be created by the pug function. You can send the 
object to be viewed as an argument on creation of the frame."""

# TODO: intercept tabbing stuff with EVT_NAVIGATION_KEY - apply/skip buttons
# TODO: apply when a control loses focus
# TODO: scroll to active control

# TODO: provide interface for creating attribute
# TODO: menu option to go to file where this is defined
# TODO: send puglist a specific list of attributes
# TODO: breakout PugListWindow into its own control derived from splitWindow
# TODO: allow personalized toolbars
# TODO: put all settings in menu

import wx

from pug.syswx.wxconstants import *
from pug.syswx.pugwindow import PugWindow

def pug_frame( obj=None, *args, **kwargs):
    """pug_frame( obj=None, *args, **kwargs) -> a PugFrame or None

Open a PugFrame, or if one exists AND control is not being held down, bring it 
to the top. For arguments, see the doc for PugFrame.  This is exactly the same, 
except if there is already a PugFrame for obj, it is brought to the front rather 
than opening a new frame."""
    app = wx.GetApp()
    if not app.show_object_pugframe(obj) or wx.GetKeyState(wx.WXK_CONTROL):
        retvalue = PugFrame(obj, *args, **kwargs)
    else:
        retvalue = None
    return retvalue

class PugFrame(wx.Frame):
    """A frame that holds a Python Universal GUI
    
PugFrame(self, obj=None, objectpath="object", title="", show=True, parent=None)
    parent: parent window
    obj: the object to view
    title: the frame title. if not provided, set_object will create one
    objectpath: relative name e.g. 'mygame.scene.player'
    show: call Show on this frame immediately
"""
    toolBar = None
    menuBar = None
    activePugWindow = None
    def __init__(self, obj=None, objectpath="unknown", title="", 
                  show=True, parent=None):        
        sizer = wx.BoxSizer()

        wx.Frame.__init__(self, parent=parent, size=WX_PUGFRAME_DEFAULT_SIZE, 
                          title=title)        
        self.SetMinSize(wx.Size(250, 130))
        
        #self.SetIcon('../Images/pug.png')
        #toolbarSeparator = wx.StaticLine(self, size=(1,2))
        #toolbarSeparator.SetMinSize((-1,-1))
        #sizer.AddWindow(toolbarSeparator, flag=wx.EXPAND)
        self.SetSizer(sizer)        
        pugWindow = PugWindow(self)
        self.set_pugwindow( pugWindow)
        self.set_pugwindow_object( obj, objectpath, title)
        bar = self.CreateStatusBar()        
        bar.Bind(wx.EVT_LEFT_DCLICK, self.show_all_attributes)        
        self.Bind(wx.EVT_MENU, self._evt_passmenu)
        self.show_all_attributes()
        if show:
            self.Show()
            
    def set_pugwindow_object(self, obj, objectpath, title):
        self.activePugWindow.set_object(obj, objectpath, title)
        self.SetTitle(self.activePugWindow.title)        
        
    def show_all_attributes(self, event = None):
        """Expand the frame's size so that all attributes are visible"""
        bestSize = self.activePugWindow.get_optimal_size()
        # give some space for scrollbars
        newSize = (bestSize[0] + WX_SCROLLBAR_FUDGE[0], 
                   bestSize[1] + WX_SCROLLBAR_FUDGE[1])
        # show the whole toolbar
        toolbarWidth = self.GetToolBar().GetSize()[0]
        if newSize[0] < toolbarWidth:
            newSize = (toolbarWidth, newSize[1])
            
        self.SetClientSize(newSize)
        self.activePugWindow.GetSizer().Layout()
            
    def _evt_passmenu(self, event):
        if self.activePugWindow:
            self.activePugWindow.ProcessEvent(event)
            
    def set_pugwindow(self, pugWindow):
        if self.activePugWindow:
            self.activePugWindow.Destroy()
        if self.toolBar:
            self.toolBar.Hide()
        if self.menuBar:
            self.menuBar.Hide()
        if pugWindow.toolBar:
            toolBar = pugWindow.toolBar
            self.SetToolBar(toolBar)
            toolBar.Show()
        if pugWindow.menuBar:
            menuBar = pugWindow.menuBar
            self.SetMenuBar(menuBar)
            menuBar.Show()
        self.GetSizer().AddWindow(pugWindow, 1, border=0, flag=wx.EXPAND)
        self.activePugWindow = pugWindow
        
    def get_object_list(self):
        """get_object_list() > list of objects displayed in this frame
"""
        return [self.activePugWindow.objectRef()]

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