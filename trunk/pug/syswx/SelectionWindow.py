# SelectionWindow.py

"""SelectionWindow

A pug window with added functionality for displaying currently selected objects.
"""
import wx

from pug.syswx.pugwindow import PugWindow

_DEBUG = False

class SelectionWindow( PugWindow):
    """SelectionWindow( parent)
    
A PugFrame that tracks the selected objects using the methods in the pug App. 
To set the viewed object, use PugApp.set_selection. 
"""
    selectionList = []
    def __init__(self, parent):
        PugWindow.__init__(self, parent)
        app = wx.GetApp()
        app.register_selection_watcher(self)
        self.on_set_selection( app.selectedObjectDict)        
        
    def on_set_selection(self, selectionDict={}):
        """on_set_selection(selectionDict={})
        
selectionDict: a dict of obj:ref for this window to display a pug view of.
Callback from PugApp...        
"""
        if _DEBUG: print "SelectionWindow.on_set_selection:",\
                                                            selectionDict.keys()
        if selectionDict:
            selectionList = selectionDict.data.keys()
        else:
            selectionList = []
        if self.selectionList == selectionList:
            self.refresh()
#            return
        self.selectionList = selectionList
        oldObject = self.object
        if not selectionList:
            self.display_message("Nothing Selected")
            self.SetTitle("Selection", False)
        elif len(selectionDict) == 1:
            obj = selectionDict.values()[0]()
            wx.CallAfter(self.set_object, obj)
        else:
            self.display_message("Multiple Objects Selected")
            self.SetTitle("Selection: Multiple", False)
            
    def on_selection_refresh(self):
        self.refresh()
        
    def SetTitle(self, title, prefix=True):
        parent = self.GetParent()
        if self.object:            
            self.titleBase = title
            if prefix:
                title = ''.join(['Selection: ',self.titleBase])
            if getattr(parent, 'SetTitle'):
                parent.SetTitle(title)
        else:
            self.titleBase = ''
            parent.SetTitle('Selection')