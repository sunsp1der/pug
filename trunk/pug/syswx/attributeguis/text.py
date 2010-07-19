"""Simple text entry attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class Text (Base):
    """Text attribute GUI is a simple text edit box
    
Text(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        control = wx.Panel(window)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        control.SetSizer(sizer)
        textEntry = wx.TextCtrl( control)
#        textEntry.SetMinSize((-1, WX_STANDARD_HEIGHT))
        sizer.Add(textEntry,1,flag=wx.EXPAND)
        textEntry.Bind(wx.EVT_TEXT_ENTER, self.apply)
        textEntry.Bind(wx.EVT_KILL_FOCUS, self.apply)
        self.textEntry = textEntry
#        textEntry = AguiTextCtrl( window)
#        control = textEntry

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        Base.setup(self, attribute, window, aguidata)
                        
    def get_control_value(self):
        return self.textEntry.GetValue()
    
    def set_control_value(self, value):
        return self.textEntry.SetValue(value)
