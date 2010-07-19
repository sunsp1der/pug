"""Font picker button that brings up Font dialog"""


### INCOMPLETE!!! ###


import wx
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class FontButton (Base):
    """FontButton agui opens a fontpicker dialog
    
FontButton(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata, **kwargs):
        control = wx.Panel(window, size=wx.Size(30, WX_STANDARD_HEIGHT))
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        picker = wx.FontPickerCtrl(control)
#        checkbox.Bind(wx.EVT_CHECKBOX, self.apply)
#        checkbox.Bind(wx.EVT_SET_FOCUS, self.focus)
#        checkbox.Bind(wx.EVT_KILL_FOCUS, self.unfocus)
        self.picker = picker
#        line = wx.StaticLine(control)
        sizer.Add(picker,1)
#       sizer.Add(line,flag=wx.EXPAND)
        control.SetSizer(sizer)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def get_control_value(self):
        return
        value = self.picker.GetValue()            
        return value
    
    def set_control_value(self, value):
        return
        return self.picker.SetValue(bool(value))
    
#    def focus(self, event=None):
#        pass
#        
#    def unfocus(self, event=None):
#        pass