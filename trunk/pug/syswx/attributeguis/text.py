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
    def __init__(self, attribute, window, **kwargs):
        control = wx.TextCtrl(window.get_control_window(), -1, 
                              size=wx.Size(30, WX_STANDARD_HEIGHT), 
                              style=wx.TAB_TRAVERSAL | wx.TE_PROCESS_ENTER)
        control.SetMinSize(wx.Size(0, WX_STANDARD_HEIGHT))
        control.Bind(wx.EVT_TEXT_ENTER, self.apply)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, **kwargs)
        
    def get_control_value(self):
        try:
            val = eval(self.control.GetValue())
        except:
            val = self.control.GetValue()
            
        return val
    
    def set_control_value(self, value):
        if (value == str(value)):
            value = repr(value)
        return self.control.SetValue(str(value))