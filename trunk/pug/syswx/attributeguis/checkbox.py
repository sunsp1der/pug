"""Simple checkbox boolean attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class Checkbox (Base):
    """Checkbox attribute GUI is your basic True/False checkbox
    
Checkbox(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, frame, **kwargs):
#        control = wx.CheckBox(frame.get_control_window(), -1, 
#                              size=wx.Size(30, WX_STANDARD_HEIGHT), 
#                              style=wx.TAB_TRAVERSAL | wx.TE_PROCESS_ENTER)
        control = wx.Panel(frame.get_control_window(),                                
                           size=wx.Size(30, WX_STANDARD_HEIGHT))
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        checkbox = wx.CheckBox(control, -1, " ")
        checkbox.Bind(wx.EVT_CHECKBOX, self.apply)
        self.checkbox = checkbox
        line = wx.StaticLine(control)
        sizer.Add(checkbox,1,wx.EXPAND)
        sizer.Add(line,flag=wx.EXPAND)
        control.SetSizer(sizer)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, frame, **kwargs)
        
    def get_control_value(self):
        value = self.checkbox.GetValue()            
        return value
    
    def set_control_value(self, value):
        return self.checkbox.SetValue(bool(value))