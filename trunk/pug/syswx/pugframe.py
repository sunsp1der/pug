"""PugFrame: The basic pug display frame

This is generally meant to be created by the pug function. You can send the 
object to be viewed as an argument on creation of the frame."""

# TODO: provide interface for creating attribute
# TODO: send aguilist a specific list of attributes

import wx


from pug.syswx.util import get_icon
from pug.syswx.wxconstants import *
from pug.syswx.pugwindow import PugWindow

def pug_frame( obj=None, *args, **kwargs):
    """pug_frame( obj=None, *args, **kwargs) -> a PugFrame or None

Open a PugFrame, or if one exists AND control is not being held down, bring it 
to the top. For arguments, see the doc for PugFrame.  This is exactly the same, 
except if there is already a window for obj, it is brought to the front rather 
than opening a new frame.
This function will create a pugApp(wx.App) if one does not exist.
"""
    newApp = False
    app = wx.GetApp()
    if not app:
        newApp = True
        from pug import App
        app = App()
    if wx.GetKeyState(wx.WXK_CONTROL) or not app.show_object_frame(obj):
        retvalue = PugFrame(obj, *args, **kwargs)
    else:
        retvalue = None
    if newApp:
        import threading
        thread = threading.Thread(target=app.MainLoop)
        thread.start()
    return retvalue

# PROGRAMMER'S WARNING: PugMDIChild derives from this, so any use of features  
# wx.Frame has but wx.aui.AuiMDIChildFrame doesn't have will create problems
# with PugMDIChild.
class PugFrame(wx.Frame):
    """A frame that holds a Python Universal GUI
    
PugFrame(self, obj=None, objectpath="object", title="", show=True, parent=None,
            name=None, **kwargs)
    obj: the object to view
    objectpath: relative name e.g. 'mygame.scene.player'
    title: the frame title. if not provided, set_object will create one
    show: call Show on this frame immediately
    parent: parent window
    name: set and lock the frame's name to this (otherwise it's name will always
        be its current title)
    kwargs: passed on to the wx.Frame.__init__
"""
    object = None
    toolBar = None
    menuBar = None
    pugWindow = None
    passingMenuEvent = None
    lockedName = None
    def __init__(self, obj=None, objectpath="unknown", title="", 
                  show=True, parent=None, name=None, **kwargs):        
        wx.Frame.__init__(self, parent=parent, size=WX_PUGFRAME_DEFAULT_SIZE, 
                          title=title, name='', **kwargs)        
        self.SetMinSize(wx.Size(250, 130))
        self.SetIcon(get_icon())
        self.objectpath = objectpath
        self.Bind(wx.EVT_ACTIVATE, self._evt_on_activate)
        self.Bind(wx.EVT_MENU, self._evt_passmenu)        
        bar = self.CreateStatusBar()        
        bar.Bind(wx.EVT_LEFT_DCLICK, self.show_all_attributes)  
        self.setup_window(obj, objectpath, title, name)
        self.Layout()
        rect = wx.GetApp().get_default_rect( self)
        if rect:
            self.SetPosition((rect[0],rect[1]))
            self.SetSize((rect[2],rect[3]))
        if show:
            self.Show()
            
    def setup_window(self, obj, objectpath, title, name):
        self.lockedName = name
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)        
        pugWindow = PugWindow(self)
        self.set_pugwindow( pugWindow)
        self.set_object( obj, objectpath, title)
        return pugWindow
            
    def _evt_on_activate(self, event=None):
        if self.pugWindow:
            if event.Active:
                self.pugWindow.refresh()
                self.Refresh()
            elif self.pugWindow.settings.get('auto_apply', False):
                self.apply()
                
    def apply(self, event=None):
        self.pugWindow.apply()
        
    def refresh(self, event=None):
        if self.pugWindow:
            self.pugWindow.refresh()
            
    def set_object(self, obj, objectpath="unknown", title=""):
        """set_object(obj, objectpath, title)
        
Set the object that this frame's pugWindow is viewing
"""
        self.Freeze()
        self.pugWindow.set_object(obj, objectpath, title)
        self.Layout()
        if not self.lockedName:
            self.Name = self.pugWindow.titleBase  
        if self.IsFrozen():                 
            self.Thaw()
        
    def get_object(self):
        return self.pugWindow.objectRef()
    
    def show_all_attributes(self, event=None):
        """Expand the frame's size so that all attributes are visible"""
        newSize = list(self.pugWindow.GetBestSize())
        # give some space for scrollbars
        newSize = [newSize[0] + WX_SCROLLBAR_FUDGE[0], 
                   newSize[1] + WX_SCROLLBAR_FUDGE[1]]
        # show the whole toolbar
        if self.GetToolBar():
            toolbarWidth = self.GetToolBar().GetSize()[0]
            if newSize[0] < toolbarWidth:
                newSize = (toolbarWidth, newSize[1])
#        if self.GetMenuBar():
#            menusize = self.GetMenuBar().GetSize()
#            newSize[1] += menusize[1]
        self.SetClientSize(newSize)
        self.Layout()
            
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
            
    def set_pugwindow(self, pugWindow):
        self.GetSizer().Clear(True)
        self.GetSizer().AddWindow(pugWindow, 1, border=0, flag=wx.EXPAND)
        self.pugWindow = pugWindow
        self.setup_tools()
        
    def setup_tools(self):
        pugWindow = self.pugWindow
        if self.toolBar:
            self.toolBar.Hide()
        if self.menuBar:
            self.menuBar.Hide()
        if hasattr(pugWindow, "toolBar"):
            toolBar = pugWindow.toolBar
            self.SetToolBar(toolBar)
            toolBar.Show()
            self.toolBar = toolBar
            toolBar.Realize()
        if hasattr(pugWindow, "menuBar"):
            menuBar = pugWindow.menuBar
            self.SetMenuBar(menuBar)
            menuBar.Show()
            self.menuBar = menuBar
        
    def get_object_list(self):
        """get_object_list() > list of objects displayed in this frame
"""
        return [self.pugWindow.objectRef()]
    
    def on_view_object_deleted(self, window, obj):
        """on_view_object_deleted(window, obj)
        
window: the PugWindow whose object was deleted
obj: the proxy object
Override this callback to affect behavior when an object being viewed in the
pugframe is deleted.
"""
        self.SetTitle(''.join(['Deleted: ', self.GetTitle()]))