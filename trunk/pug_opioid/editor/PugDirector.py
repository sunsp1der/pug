"""PugDirector.py

Hack in a few features necessary for the Opioid2D director to work with pug"""

import wx
import time
import Opioid2D
from Opioid2D.internal.objectmgr import ObjectManager
from Opioid2D.public.Image import ImageMeta
from Opioid2D.public.ResourceManager import ResourceManager
import sys, traceback

#hack for quitting pug when opioid quits
QUITTING = False
def pug_opioid_quit(*args, **kwargs):
    """pug_opioid_quit(*args, **kwargs)
    
Have the app confirm project closure.
"""
    if not wx.GetApp():
        Opioid2D.Director.realquit()
        return
    global QUITTING
    if not QUITTING:
        QUITTING = True
        app = wx.GetApp()
        if hasattr(app, '_evt_project_frame_close'):
            wx.CallAfter(app._evt_project_frame_close)
        return 
# set up our special quit
Opioid2D.Director.realquit = Opioid2D.Director.quit
Opioid2D.Director.quit = pug_opioid_quit # hack to make opioid quit=pugquit 
