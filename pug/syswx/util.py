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

def open_shell( rootObject=None, rootLabel=None, locals=None, 
                clean_pages=True, title='Pug Shell', icon=None,
                pugViewKey=None):
    """open_shell(rootObject=None,rootLabel=None,locals=None...
                    clean_pages=True, title='Pug Shell', icon=None):

rootObject: the root object of shell tree. A dict of objects also works nicely.
rootLabel: the label for the root object
locals: the locals available in the shell
clean_pages: if True, remove the Display, Calltip, and Dispatcher pages
title: window title
icon: defaults to pug icon
pugViewKey: this is the main viewing object for this frame. Used by pug to
    determine if duplicate shells are being opened. Defaults to rootObject.
    It will be converted to a tuple: (weakref.ref(pugViewKey),"shell") and
    stored as the 'pugViewKey' field of the shell frame.

This opens a PyCrust shell for realtime editing of your object. If a shell for
the given object is already open, it is raised instead unless ctrl is held down.
Objects can over-ride arguments by returning a dictionary of them from 
_get_shell_info()
"""
    app = wx.GetApp()
    if pugViewKey is None:
        pugViewKey = rootObject
    pug_key = (weakref.ref(pugViewKey),"shell")
    if app.show_object_frame(pug_key):
        # we already have a shell open for this object
        return
    from wx.py.crust import CrustFrame
    c = CrustFrame(locals=locals,rootObject=rootObject, rootLabel=rootLabel,
                   title=title)
    if clean_pages:
        c.crust.notebook.RemovePage(4)
        c.crust.notebook.RemovePage(2)
        c.crust.notebook.RemovePage(1)
    if icon is None:
        icon = get_icon()
    c.pugViewKey = pug_key
    c.SetIcon(icon)
    app.frame_viewing( c, pug_key)
    c.Show()

class TestEventHandler( wx.EvtHandler):
    def __init__(self, *args, **kwargs):
        wx.EvtHandler.__init__(self, *args, **kwargs)
    def ProcessEvent(self, event):
        print event
        
def get_icon():
    return wx.Icon( get_image_path('pug.ico'), wx.BITMAP_TYPE_ICO)

def show_exception_dialog( parent=None, prefix='', exc_info=None):
    """ExceptionDialog(parent=None, prefix='')

show exception info in a dialog
parent: parent frame
prefix: show in title of window before exception type
exc_info: if provided, this is the data from sys.exc_info(). If not, use the
    current sys.exc_info()
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
    err.ShowModal()
    err.Destroy()
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
        