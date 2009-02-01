import traceback
from sys import exc_info

import wx
from wx.lib.dialogs import ScrolledMessageDialog

from pug.util import get_image_path
from pug.pugview_manager import get_default_pugview
import pug.aguilist

_DEBUG = False

class TestEventHandler( wx.EvtHandler):
    def __init__(self, *args, **kwargs):
        wx.EvtHandler.__init__(self, *args, **kwargs)
    def ProcessEvent(self, event):
        print event
        
def get_icon():
    return wx.Icon( get_image_path('pug.ico'), wx.BITMAP_TYPE_ICO)

def show_exception_dialog( parent=None):
    """ExceptionDialog(parent): show exception info in a dialog"""
    info = exc_info()
    err = ScrolledMessageDialog(parent, 
                                   str(traceback.format_exc()),
                                   info[0].__name__,
                                   size=(500, 220))
    # scroll to bottom
    err.Children[0].ShowPosition(len(traceback.format_exc()))
    err.ShowModal()
    err.Destroy()

def cache_aguilist( aguilist):
    for agui in aguilist:
        cache_agui(agui)

_DUMMYFRAME = None
def get_dummyframe():
    global _DUMMYFRAME
    if not _DUMMYFRAME:
        from pug import frame
        obj = object()
        _DUMMYFRAME = wx.Frame(None)
        _DUMMYFRAME.object = obj
    return _DUMMYFRAME
        
def cache_agui( agui):
    dummy = get_dummyframe()
    try:
        agui.control.Freeze()
        agui.label.Freeze()
        agui.control.Reparent(dummy)
        agui.label.Reparent(dummy)
    except:
        pass
    else:
        if _DEBUG: print 'cache_agui',agui
        if agui.control.GetParent() == agui.label.GetParent() == dummy:
            pug.aguilist.cache_agui(agui)
            
def cache_default_view( obj):
    dummy = get_dummyframe()
    dummy.object = obj
    try:
        # hide the cache so we don't use it
        cacheStash = pug.aguilist.aguiCache
        cache = pug.aguilist.aguiCache = {}
        aguilist = pug.aguilist.create_aguilist( obj, dummy)
        for agui in aguilist:
            try:
                cache_agui( agui)
            except:
                continue
        for cls, list in cacheStash.iteritems():
            if cache.get(cls, False):
                cache[cls] += cacheStash[cls]
            else:
                cache[cls] = cacheStash[cls]
    except:
        pass
        