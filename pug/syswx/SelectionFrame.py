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
        PugFrame.__init__(self, *args, **kwargs)
        
    def on_set_selection(self, selectionRefSet=None):
        """on_set_selection(selectionRefSet=None)
        
selectionRefSet: a set of references for this frame to display a pug view of.
Callback from PugApp...        
"""
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
            self.activePugWindow.set_object(obj)
            self.SetTitle(''.join(['Selection: ',self.activePugWindow.title]))
            selectionRefSet.add(objRef)
        else:
            self.activePugWindow.display_message("Multiple Objects Selected")
            self.SetTitle("Selection: Multiple")
            #TODO: make this work
        if not oldObject:
            self.show_all_attributes()
            
    def on_view_object_deleted(self, window, obj):
        """on_view_object_deleted( window, obj)
        
An object being viewed here has been deleted. Callback from PugWindow...
"""
        wx.GetApp().set_selection()