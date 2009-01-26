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
        PugWindow.__init__(self, parent)
        app = wx.GetApp()
        app.register_selection_watcher(self)
        self.on_set_selection( app.selectedRefSet)        
        
    def on_set_selection(self, selectionRefSet=None):
        """on_set_selection(selectionRefSet=None)
        
selectionRefSet: a set of references for this window to display a pug view of.
Callback from PugApp...        
"""
        if self.selectionRefSet == selectionRefSet:
            self.refresh()
            return
        self.selectionRefSet = selectionRefSet.copy()
        oldObject = self.object
        if not selectionRefSet:
            self.display_message("Nothing Selected")
            self.SetTitle("Selection", False)
        elif len(selectionRefSet) == 1:
            objRef = selectionRefSet.pop()
            obj = objRef()
            wx.CallAfter(self.set_object, obj)
            selectionRefSet.add(objRef)
        else:
            self.display_message("Multiple Objects Selected")
            self.SetTitle("Selection: Multiple", False)
            
    def on_selection_refresh(self):
        self.refresh()
        
    def SetTitle(self, title, prefix=True):
        self.titleBase = title
        parent = self.GetParent()
        if prefix:
            title = ''.join(['Selection: ',self.titleBase])
        if getattr(parent, 'SetTitle'):
            parent.SetTitle(title)