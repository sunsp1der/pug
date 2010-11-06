"""Simple text entry attribute gui"""

import wx

from pug.syswx.wxconstants import *
from pug.syswx.agui_text_ctrl import AguiTextCtrl
from pug.syswx.attributeguis.base import Base

class Generic (Base):
    """Generic attribute GUI is a text edit box that is type adaptable
    
Generic(attribute, frame, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugWindow
aguidata: additional attribute gui data...
    'do_typecast': typecast entered value to attribute's current type 
    'format_floats': round floats to 3 decimal places. 
                    defaults to pug.constants.FORMAT_FLOATS
For more aguidata optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        control = wx.Panel(window)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        control.SetSizer(sizer)
        textEntry = AguiTextCtrl( control, aguidata.get('format_floats',None))
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
        aguidata.setdefault('do_typecast',True)
        Base.setup(self, attribute, window, aguidata)
                        
    def get_control_value(self):
        return self.textEntry.GetValue()
    
    def set_control_value(self, value):
        return self.textEntry.SetValue(value)
    
    def set_attribute_value(self):
        """set_attribute_value()->False if there was a problem. True otherwise.
        
Try to set the aguis attribute to the value shown in the control
"""
        try:
            control_value = self.get_control_value()
            attribute_value = self.get_attribute_value()
        except:
            return False
        if attribute_value is None: 
            # attribute type not set
            try:
                setattr(self.window.object,self.attribute,control_value)
            except:
                return False
            else:
                return True                  
        else:
            try:
                if self.aguidata['do_typecast'] is False or \
                        (type(attribute_value) == int and \
                            type(control_value) == float):
                    typedValue = control_value 
                elif type(attribute_value) in BASIC_TYPES and \
                                                    control_value is not None:
                # if we have a basic attribute type, and we're not setting 
                # to None, typecast our control_value to the attribute 
                # value's current type
                    typedValue = type(attribute_value)(control_value)
                else:
                    # no type-casting for special types... don't want any 
                    # weird garbage sitting around
                    typedValue = control_value
                setattr(self.window.object, self.attribute, typedValue)              
            except:
                return False
            else:
                return True        
            