"Drag n drop functionality"

import weakref

import wx

# Define File Drop Target class
class FileDropTarget(wx.FileDropTarget):
    """This object implements Drop Target functionality for Files"""
    obj = None
    def __init__(self, obj):
        """FileDropTarget( obj) 

call obj.on_drop_files(x, y, filenames) when file dropped"""
        wx.FileDropTarget.__init__(self)
        self.obj = weakref.ref(obj)

    def OnDropFiles(self, x, y, filenames):
        "OnDropFiles(x, y, filenames): filenames is a list"
        obj = self.obj()
        if not obj:
            return
        obj.on_drop_files( x, y, filenames)



