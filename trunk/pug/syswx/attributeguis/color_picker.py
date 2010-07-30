"""Color picker attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class ColorPicker (Base):
    """Color picker attribute GUI is a button for picking an r,g,b color. The
RGB values range from zero to one.
    
ColorPicker(attribute, frame, aguidata, **kwargs). 
attribute: what attribute of window.object is being controlled
window: the parent pugWindow
aguidata: additional attribute gui data...
    'text_control': Use a text control to display the text form of the color
    'show_label': show the color hex value as RRGGBB in the button's label
    'return_alpha': returns a fourth value in the color tuple. Alpha is ALWAYS 1
For more aguidata optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        control = wx.Panel(window)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        control.SetSizer(sizer)
        
        style = 0
        if aguidata.get('text_control', False):
            style = style | wx.CLRP_USE_TEXTCTRL
        if aguidata.get('show_label', False):
            style = style | wx.CLRP_SHOW_LABEL
        colorPicker = wx.ColourPickerCtrl( control, style=style)

        if aguidata.get('text_control', False):
            colorPicker.SetTextCtrlProportion( 1)
#        textEntry.SetMinSize((-1, WX_STANDARD_HEIGHT))
        sizer.Add(colorPicker,1,flag=wx.EXPAND)
        colorPicker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.apply)
        colorPicker.Bind(wx.EVT_KILL_FOCUS, self.apply)
        self.colorPicker = colorPicker
#        textEntry = AguiTextCtrl( window)
#        control = textEntry

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        Base.setup(self, attribute, window, aguidata)
                        
    def get_control_value(self):
        color = self.colorPicker.GetColour()
        color = (color[0], color[1], color[2], 1.0)
        if not self.aguidata.get('return_alpha', False):
            color = (color[0], color[1], color[2])
        return color
    
    def set_control_value(self, value):
        value = (value[0], value[1], value[2])            
        return self.colorPicker.SetColour(value)
           
            