import traceback
from sys import exc_info

import wx
from wx.lib.dialogs import ScrolledMessageDialog


from pug.util import imagePath

class TestEventHandler( wx.EvtHandler):
    def __init__(self, *args, **kwargs):
        wx.EvtHandler.__init__(self, *args, **kwargs)
    def ProcessEvent(self, event):
        print event
        
def get_icon():
    return wx.Icon( imagePath('pug.ico'), wx.BITMAP_TYPE_ICO)

def ShowExceptionDialog( parent=None):
    """ExceptionDialog(parent): show exception info in a dialog"""
    info = exc_info()
    err = ScrolledMessageDialog(parent, 
                                   str(traceback.format_exc()),
                                   info[0].__name__,
                                   size=(500, 120))
    # scroll to bottom
    err.Children[0].ShowPosition(len(traceback.format_exc()))
    err.ShowModal()
    err.Destroy()
