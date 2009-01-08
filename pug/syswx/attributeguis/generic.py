"""Simple text entry attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.agui_text_ctrl import AguiTextCtrl
from pug.syswx.attributeguis.base import Base

class Generic (Base):
    """Generic attribute GUI is a text edit box that is type adaptable
    
Generic(attribute, frame, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugWindow
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, **kwargs):
        #control = wx.Panel(window.get_control_window())
        #sizer = wx.BoxSizer()
        textEntry = AguiTextCtrl( window.get_control_window())
        #control.SetSize((30, WX_STANDARD_HEIGHT))
        #sizer.Add(textEntry,1,flag=wx.EXPAND)
        #control.SetSizer(sizer, orient=wx.VERTICAL)
        textEntry.Bind(wx.EVT_TEXT_ENTER, self.apply)
        textEntry.Bind(wx.EVT_KILL_FOCUS, self.apply)

        kwargs['control_widget'] = textEntry
        Base.__init__(self, attribute, window, **kwargs)
                        
    def get_control_value(self):
        return self.control.GetValue()
    
    def set_control_value(self, value):
        return self.control.SetValue(value)
           
            