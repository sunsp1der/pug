"""play_buttons.py"""
from inspect import isroutine

import wx
import wx.lib.buttons as buttons

from pug.syswx.wxconstants import *
from pug.syswx.util import show_exception_dialog
from pug.syswx.attributeguis.base import Base
from pug.syswx.agui_label_sizer import AguiLabelSizer

class PlayButtons (Base):
    """An attribute gui with Rewind, Play, Pause, Stop, FastForward buttons

PlayButtons(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugWindow. 
aguidata: {
    'rewind': the function to run on Rewind press
    'play': the function to run on Play press
    'pause': the function to run on Pause press
    'stop': the function to run on Stop press
    'fast_forward': the function to run on Fast Forward press
    'execute': the function to run on Execute press
    }
    
    If functions are not defined, button will not be shown.
    If functions are strings, they will be converted to methods of the object 
        being viewed.
For kwargs arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata ={}, **kwargs):
        #widgets
        control = wx.Panel(window, 
                           size=(1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1, WX_STANDARD_HEIGHT))
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        control.SetSizer(controlSizer)

        buttonOrder = ['rewind', 'play', 'pause', 'stop', 'fast_forward', 
                       'execute']
        buttonDict = {
                'rewind':('Rewind', wx.ArtProvider.GetBitmap(wx.ART_UNDO,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)),
                'play':('Play', wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)),
                'pause':('Pause',wx.ArtProvider.GetBitmap(wx.ART_WARNING,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)),
                'stop':('Stop',wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)),
                'fast_forward':('Fast Forward', 
                                wx.ArtProvider.GetBitmap(wx.ART_REDO,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)),
                'execute':('Execute in separate process', 
                                wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE,
                                        wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)),
                }
                
        self.functionDict = {}
        
        for item in buttonOrder:
            info = buttonDict[item]
            if not aguidata.has_key(item):
                continue
            if isroutine(aguidata[item]):
                func = aguidata[item]
            else:
                func = getattr( window.object, aguidata[item], None)
                if not isroutine(func):
                    continue
            button = buttons.ThemedGenBitmapButton(control, size=WX_BUTTON_SIZE)
            button.SetBitmapLabel(info[1])
            self.functionDict[button] = func    
            button.SetToolTipString(info[0])
            control.Bind(wx.EVT_BUTTON, self.button_press, button)
            controlSizer.Add( button)
        line = AguiLabelSizer(control, ' ')
        controlSizer.Add(line, 1)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs) 
        
    def setup(self, attribute, window, aguidata):
        if self.aguidata != aguidata:
            self.control.Destroy()
            self.label.Destroy()
            self.__init__(attribute, window, aguidata)
            return
        else:
            Base.setup( self, attribute, window, aguidata)        
        
    def button_press(self, event):  
        """Call the appropriate function"""
        try:
            self.functionDict[event.GetEventObject()]()
        except:
            show_exception_dialog(self.control)
            wx.StopBusyCursor()
        self.refresh_window()
