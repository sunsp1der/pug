"""Simple checkbox boolean attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class Checkbox (Base):
    """Checkbox attribute GUI is your basic True/False checkbox
    
Checkbox(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata, **kwargs):
        control = wx.Panel(window, size=wx.Size(30, WX_STANDARD_HEIGHT))
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        checkbox = wx.CheckBox(control, -1, label=" ")
        checkbox.Bind(wx.EVT_CHECKBOX, self.apply)
        checkbox.Bind(wx.EVT_SET_FOCUS, self.focus)
        checkbox.Bind(wx.EVT_KILL_FOCUS, self.unfocus)
        self.checkbox = checkbox
        line = wx.StaticLine(control)
        sizer.Add(checkbox,1)
        sizer.Add(line,flag=wx.EXPAND)
        control.SetSizer(sizer)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def get_control_value(self):
        value = self.checkbox.GetValue()            
        return value
    
    def set_control_value(self, value):
        return self.checkbox.SetValue(bool(value))
    
    def focus(self, event=None):
        pass
        
    def unfocus(self, event=None):
        pass