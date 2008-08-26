import wx
from pug.util import imagePath

class TestEventHandler( wx.EvtHandler):
    def __init__(self, *args, **kwargs):
        wx.EvtHandler.__init__(self, *args, **kwargs)
    def ProcessEvent(self, event):
        print event
        
def get_icon():
    return wx.Icon( imagePath('pug.ico'), wx.BITMAP_TYPE_ICO)

