# SelectionFrame.py

"""SelectionFrame 

A pug frame with added functionality for displaying currently selected objects.
"""
import wx

from pug.syswx.pugframe import PugFrame

class SelectionFrame( PugFrame):
    """SelectionFrame( *args, **kwargs)
    
WARNING: this object is meant to be created using PugApp.open_selection_frame.
A PugFrame that tracks the selected objects using the methods in the pug App. 
*args and **kwargs are passed to PugFrame.__init__. 
"""
    selectionRefSet = None
    def __init__(self, *args, **kwargs):
        kwargs['title'] = 'Selection'
        PugFrame.__init__(self, *args, **kwargs)
        
    def on_set_selection(self, selectionRefSet=None):
        """on_set_selection(selectionRefSet=None)
        
selectionRefSet: a set of references for this frame to display a pug view of.
Callback from PugApp...        
"""
        if not self.activePugWindow:
            return
        if self.selectionRefSet == selectionRefSet:
            self.activePugWindow.refresh_all()
            return
        self.selectionRefSet = selectionRefSet.copy()
        oldObject = self.activePugWindow.object
        if not selectionRefSet:
            self.activePugWindow.display_message("Nothing Selected")
            self.SetTitle("Selection")
        elif len(selectionRefSet) == 1:
            objRef = selectionRefSet.pop()
            obj = objRef()
            wx.CallAfter(self.set_object, obj)
            selectionRefSet.add(objRef)
        else:
            self.activePugWindow.display_message("Multiple Objects Selected")
            self.SetTitle("Selection: Multiple")
            #TODO: make this work
            
    def on_selection_refresh(self):
        if self.activePugWindow:
            self.activePugWindow.refresh_all()
            
    def set_object(self, obj, objectpath="unknown", title=""):
        """set_object(*args, **kwargs)
        
same as pugframe set_object except the title is prepended with 'Selection: '
"""
        PugFrame.set_object(self, obj, objectpath, title)
        title = ''.join(['Selection: ',self.activePugWindow.title])
        self.SetTitle(title)
        self.Name = "Selection"
       
    def on_view_object_deleted(self, window, obj):
        """on_view_object_deleted( window, obj)
        
An object being viewed here has been deleted. Callback from PugWindow...
"""
        wx.GetApp().set_selection()