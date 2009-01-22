# SelectionWindow.py

"""SelectionWindow

A pug window with added functionality for displaying currently selected objects.
"""
import wx

from pug.syswx.pugwindow import PugWindow

class SelectionWindow( PugWindow):
    """SelectionWindow( parent)
    
A PugFrame that tracks the selected objects using the methods in the pug App. 
To set the viewed object, use PugApp.set_selection. 
"""
    selectionRefSet = None
    def __init__(self, parent):
        PugWindow.__init__(self, parent, title='Selection')
        app = wx.GetApp()
        app.register_selection_watcher(self)
        self.on_set_selection( app.selectedRefSet)        
        
    def on_set_selection(self, selectionRefSet=None):
        """on_set_selection(selectionRefSet=None)
        
selectionRefSet: a set of references for this window to display a pug view of.
Callback from PugApp...        
"""
        if self.selectionRefSet == selectionRefSet:
            self.refresh_all()
            return
        self.selectionRefSet = selectionRefSet.copy()
        oldObject = self.object
        if not selectionRefSet:
            self.display_message("Nothing Selected")
            self.SetTitle("Selection")
        elif len(selectionRefSet) == 1:
            objRef = selectionRefSet.pop()
            obj = objRef()
            wx.CallAfter(self.set_object, obj)
            selectionRefSet.add(objRef)
        else:
            self.display_message("Multiple Objects Selected")
            self.SetTitle("Selection: Multiple")
            
    def on_selection_refresh(self):
        self.refresh_all()
            
    def set_object(self, obj, objectpath="unknown", title=""):
        """set_object(*args, **kwargs)
        
same as pugframe set_object except the title is prepended with 'Selection: '
"""
        PugWindow.set_object(self, obj, objectpath, title)
        title = ''.join(['Selection: ',self.title])
        self.SetTitle(title)
        self.Name = "Selection"
       