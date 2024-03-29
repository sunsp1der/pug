import traceback
import sys
import os
import weakref

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
        
def highlight_frame( frame):        
    "highlight_frame(frame): If frame ishidden, show/raise else raise/flash"
    shown = frame.IsShown()
    frame.Show()
    if frame.IsIconized():
        frame.Iconize(False)
    frame.Raise()
    if not shown:
        frame.RequestUserAttention()
        
def get_icon():
    "get_icon()->The wx.Icon for pug"
    return wx.Icon( get_image_path('pug.ico'), wx.BITMAP_TYPE_ICO)

def show_exception_dialog( parent=None, prefix='', exc_info=None, modal=False):
    """ExceptionDialog(parent=None, prefix='', exc_info=None)

show exception info in a dialog
parent: parent frame
prefix: show in title of window before exception type
exc_info: if provided, this is the data from sys.exc_info(). If not, use the
    current sys.exc_info()
modal: if True, show dialog as a modal dialog
"""
    if exc_info is None:
        info = sys.exc_info()
    else:
        info = exc_info
    if parent is None:
        parent = wx.GetApp().get_project_frame()
    filepath = traceback.extract_tb(info[2])[-1:][0][0]
    try:
        title = prefix + info[0].__name__ + ' in ' + os.path.split(filepath)[1]
    except:
        title = prefix + info[0].__name__
    msg = traceback.format_exception(info[0], info[1], info[2])
    msg = ''.join(msg)
    err = ScrolledMessageDialog(parent, msg, title, size=(640, 320),
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    # scroll to bottom
    err.Children[0].ShowPosition(len(msg))
    if modal:
        err.ShowModal()
    else:
        err.Show()
    wx.Bell()
    return 

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
        

def close_obj_windows( obj):
    """close_obj_windows( obj)
    
Close all windows showing obj and windows for all components belonging to it.
"""
    from pug.component import Component
    app = wx.GetApp()
    for frame in app.objFrameDict:
        if hasattr(frame,'pug_view_key'):
            try:
                frameObj = frame.pug_view_key[0]()
            except:
                continue
        elif not hasattr(frame,'pugWindow'):
            continue
        else:
            if not bool(frame):
                continue
            try:
                frameObj = frame.pugWindow.objectRef()
            except:
                continue
        doclose = False
        if frameObj == obj:
            doclose = True
        elif isinstance(frameObj, Component):
            if frameObj.owner == obj:
                doclose = True
        if doclose:
            frame.Close()
    if obj in app.selectedObjectDict:
        selection = app.selectedObjectDict.keys()
        selection.remove(obj)
        app.set_selection(selection)