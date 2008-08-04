"""Simple text entry attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.agui_text_ctrl import AguiTextCtrl
from pug.syswx.attributeguis.base import Base

class Generic (Base):
    """Generic attribute GUI is a text edit box that is type adaptable
    
Generic(attribute, frame, **kwargs)
attribute: what attribute of window.object is being controlled
frame: the parent pugFrame
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, frame, **kwargs):
        control = AguiTextCtrl( frame.get_control_window())
        control.Bind(wx.EVT_TEXT_ENTER, self.apply)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, frame, **kwargs)
        
    def get_control_value(self):
        return self.control.GetValue()
    
    def set_control_value(self, value):
        return self.control.SetValue(value)
           
            