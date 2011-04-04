"""Simple text entry attribute gui"""

import wx
import wx.lib.agw.floatspin as FS

from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base
from pug.util import prettify_float

class FloatSpin (Base):
    """FloatSpin attribute GUI is a box with spinners for float numbers. 
    
Increment, format, and min/max values can be set. For speed's sake, this agui
has aguidata['refresh_all'] set to false by default. If you need the entire pug
view to refresh when the value is changed, set 'refresh_all' to True. 
    
FloatSpin(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: {
    'increment':amount that the spin buttons change value (default 0.1),
    'range': (minimum value, maximum value) (default (None,None)), 
    'format':format to display float ("%e", "%f", "%G") etc.  (default %f),
    'digits':digits to display (default 3),
    'adjust_digits': True = adjust digits to value precision (default False),
    }

For more aguidata optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        control = wx.Panel(window)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        control.SetSizer(sizer)
        floatspin = FS.FloatSpin(control, agwStyle = FS.FS_LEFT)
        sizer.Add(floatspin,1,flag=wx.EXPAND)
        floatspin.Bind(wx.EVT_TEXT_ENTER, self.enter)
        floatspin.GetTextCtrl().Bind(wx.EVT_SET_FOCUS, self.enter)
        floatspin.GetTextCtrl().Bind(wx.EVT_KILL_FOCUS, self.exit)
        floatspin.Bind(FS.EVT_FLOATSPIN, self.apply)
        self.floatspin = floatspin
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        #self.floatspin.SetRange( *self.aguidata.get('range',(None,None)))
        self.minval, self.maxval = self.aguidata.get('range',(None,None))
        self.floatspin.SetIncrement(self.aguidata.get('increment',0.1))
        self.floatspin.SetFormat(self.aguidata.get('format',"%f"))
        self.floatspin.SetDigits(self.aguidata.get('digits',2))
        Base.setup(self, attribute, window, aguidata)
                        
    def get_control_value(self):
        return self.floatspin.GetValue()
    
    def enter(self, event):
        self.floatspin.SetValue( float(self.floatspin.GetTextCtrl().GetValue()))
#        self.apply(event)    
        self.floatspin.GetTextCtrl().SelectAll()
        
    def exit(self, event):
        oldvalue = self.floatspin.GetValue()
        self.floatspin.SetValue( float(self.floatspin.GetTextCtrl().GetValue()))
        try:
            self.apply()
        except:
            self.floatspin.SetValue(oldvalue)
    
    def fix(self, event=None):
        "fix problem with showing out of range values"
        value = self.floatspin.GetValue()
        if self.minval is not None and value < self.minval:
            self.floatspin.SetValue(self.minval)
        elif self.maxval is not None and value > self.maxval:
            self.floatspin.SetValue(self.maxval)
    
    def apply(self, event=None):
        self.fix()
        if self.aguidata.get('adjust_digits', False):
            value = self.floatspin.GetValue()
            f = prettify_float(value)
            precision = len(f) - f.find('.') - 1
            if precision > self.floatspin.GetDigits():
                self.floatspin.SetDigits(precision)
        Base.apply(self, event)  
        self.floatspin.GetTextCtrl().SetSelection(0,0)
    
    def set_control_value(self, value):
        return self.floatspin.SetValue(value)
