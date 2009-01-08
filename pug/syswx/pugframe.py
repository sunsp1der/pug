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

from pug.syswx.util import get_icon
from pug.syswx.wxconstants import *
from pug.syswx.pugwindow import PugWindow

def pug_frame( obj=None, *args, **kwargs):
    """pug_frame( obj=None, *args, **kwargs) -> a PugFrame or None

Open a PugFrame, or if one exists AND control is not being held down, bring it 
to the top. For arguments, see the doc for PugFrame.  This is exactly the same, 
except if there is already a PugFrame for obj, it is brought to the front rather 
than opening a new frame.
This function will create a pugApp(wx.App) if one does not exist.
"""
    newApp = False
    app = wx.GetApp()
    if not app:
        newApp = True
        from pug import App
        app = App()
    if not app.show_object_pugframe(obj) or wx.GetKeyState(wx.WXK_CONTROL):
        retvalue = PugFrame(obj, *args, **kwargs)
    else:
        retvalue = None
    if newApp:
        import threading
        thread = threading.Thread(target=app.MainLoop)
        thread.start()
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
    passingMenuEvent = None
    def __init__(self, obj=None, objectpath="unknown", title="", 
                  show=True, parent=None, **kwargs):        
        sizer = wx.BoxSizer()
        self.lockedName = kwargs.get('name',False)
        wx.Frame.__init__(self, parent=parent, size=WX_PUGFRAME_DEFAULT_SIZE, 
                          title=title,**kwargs)        
        self.SetMinSize(wx.Size(250, 130))
        self.SetIcon(get_icon())
        self.objectpath = objectpath
        self.title = title
        self.Bind(wx.EVT_CLOSE, self._evt_on_close)
        self.Bind(wx.EVT_ACTIVATE, self._evt_on_activate)
#        toolbarSeparator = wx.StaticLine(self, size=(1,2))
#        toolbarSeparator.SetMinSize((-1,-1))
#        sizer.AddWindow(toolbarSeparator, flag=wx.EXPAND)
        self.SetSizer(sizer)        
        pugWindow = PugWindow(self)
        self.set_pugwindow( pugWindow)
        self.set_object( obj, objectpath, title)
        bar = self.CreateStatusBar()        
        bar.Bind(wx.EVT_LEFT_DCLICK, self.show_all_attributes)        
        self.Bind(wx.EVT_MENU, self._evt_passmenu)
        wx.GetApp().set_default_pos( self)
        if show:
            self.Show()
            
    def _evt_on_close(self, event=None):
        if self.activePugWindow:
            self.activePugWindow._evt_on_close()
        if event:
            event.Skip()
            
    def _evt_on_activate(self, event=None):
        if self.activePugWindow:
            if event.Active:
                self.activePugWindow.refresh_all()
            else:
                if self.activePugWindow.settings['auto_apply']:
                    self.activePugWindow.apply_all()
            
    def set_object(self, obj, objectpath="unknown", title=""):
        """set_object(obj, objectpath, title)
        
Set the object that this frame's activePugWindow is viewing
"""
        oldObject = self.activePugWindow.object
        self.Freeze()
        self.activePugWindow.set_object(obj, objectpath, title)
        self.SetTitle(self.activePugWindow.title)
        if not self.lockedName:
            self.Name = self.Title        
        if not oldObject:
            self.show_all_attributes()        
        self.Thaw()
        
    def show_all_attributes(self, event=None):
        """Expand the frame's size so that all attributes are visible"""
        bestSize = self.activePugWindow.get_optimal_size()
        if event == None:
            # called from frame, before toolbar is properly processed
            toolbarFudge = self.ToolBar.Size[1]
        else:
            toolbarFudge = 0
        # give some space for scrollbars
        newSize = (bestSize[0] + WX_SCROLLBAR_FUDGE[0], 
                   bestSize[1] + WX_SCROLLBAR_FUDGE[1] + toolbarFudge)
        # show the whole toolbar
        toolbarWidth = self.GetToolBar().GetSize()[0]
        if newSize[0] < toolbarWidth:
            newSize = (toolbarWidth, newSize[1])
        self.SetClientSize(newSize)
        self.activePugWindow.GetSizer().Layout()
            
    def _evt_passmenu(self, event): 
        # this checking stuff is necessary so that we don't have an infinite
        # recursion with us passing event down then it getting passed up again
        if self.passingMenuEvent:
            self.passingMenuEvent = None
            event.Skip()
        else:
            self.passingMenuEvent = event
            if self.activePugWindow:
                self.activePugWindow.ProcessEvent(event)
        self.passingMenuEvent = None
            
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
            self.toolBar = toolBar
            toolBar.Realize()
        if pugWindow.menuBar:
            menuBar = pugWindow.menuBar
            self.SetMenuBar(menuBar)
            menuBar.Show()
            self.menuBar = menuBar
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