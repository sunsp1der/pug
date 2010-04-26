"""PigDirector.py

Hack in a few features necessary for the Opioid2D director to work with pug"""
import threading

import wx

import Opioid2D

opioid_quit = Opioid2D.Director.quit
PigDirector = Opioid2D.Director

# this presents incorrect scene errors in code
PigDirector.scene = None

#hack for quitting pug when opioid quits
QUITTING = False
def pig_quit( query=True):
    """pig_quit( query=True)
    
query: if True, have the app confirm project closure.
"""
    if not wx.GetApp() or \
                not getattr(wx.GetApp().projectObject,'_initialized', False): 
        real_quit()
        return
    global QUITTING
    if not QUITTING:
        QUITTING = True
        app = wx.GetApp()
        if hasattr(app, '_evt_project_frame_close'):
            wx.CallAfter(app._evt_project_frame_close, query=query)
        return 
# set up our special quit
def real_quit():
    global QUITTING    
    wx.GetApp().get_project_object().kill_subprocesses()
    if not QUITTING:
        opioid_quit()
    QUITTING = True
    

PigDirector.quit = pig_quit # hack to make opioid quit=pugquit 
PigDirector.realquit = real_quit


