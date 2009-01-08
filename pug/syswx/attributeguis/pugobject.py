import re

import wx

from pug.util import get_type_name
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base
from pug.syswx.pugbutton import PugButton

class PugObject (Base):
    """An attribute gui that lets the user open pug windows to view data

PugObject(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame. 
For kwargs arguments, see the Base attribute GUI

Contains text showing attribute's value and two buttons... 
    viewButton: changes the parent window to display this object
    newViewButton: opens a new pug window to display objet
    
This control is generally meant to be used for instances, but could be used for
any object.
"""
    def __init__(self, attribute, window, **kwargs):
        #widgets
        control = wx.Panel(window.get_control_window(), 
                           size = (1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        viewButton = PugButton(control, getattr(window.object,attribute),
                               False, attribute, window)
        newViewButton = PugButton(control, getattr(window.object,attribute),
                               True, attribute, window)
        infoText = wx.StaticText(control)
        infoText.SetMinSize((-1,infoText.Size[1]))
        line = wx.StaticLine(control, style = 0) 
        self.viewButton = viewButton
        self.newViewButton = newViewButton 
        self.infoText = infoText

        # sizers
        textSizer = wx.BoxSizer(orient=wx.VERTICAL)
        textSizer.AddSpacer((1,WX_TEXTEDIT_LABEL_YOFFSET))
        textSizer.Add(infoText, 1)
        textSizer.Add(line, flag = wx.EXPAND | wx.BOTTOM)
        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        control.SetSizer(controlSizer)
        controlSizer.AddMany([(viewButton), (newViewButton)])
        controlSizer.AddSpacer((3,3))        
        controlSizer.Add(textSizer,1)
        control.sizer = controlSizer
        control.textSizer = textSizer

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, **kwargs)
        
    def set_control_value(self, val):
        self.infoText.SetLabel(get_type_name(val))                
