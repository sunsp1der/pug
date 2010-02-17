"""PigDirector.py

Hack in a few features necessary for the Opioid2D director to work with pug"""

import wx
import Opioid2D

PigDirector = Opioid2D.Director

#hack for quitting pug when opioid quits
QUITTING = False
def pig_quit(*args, **kwargs):
    """pig_quit(*args, **kwargs)
    
Have the app confirm project closure.
"""
    if not wx.GetApp() or \
                not getattr(wx.GetApp().projectObject,'_initialized', False): 
        PigDirector.realquit()
        return
    global QUITTING
    if not QUITTING:
        QUITTING = True
        app = wx.GetApp()
        if hasattr(app, '_evt_project_frame_close'):
            wx.CallAfter(app._evt_project_frame_close)
        return 
# set up our special quit
PigDirector.realquit = Opioid2D.Director.quit
PigDirector.quit = pig_quit # hack to make opioid quit=pugquit 



