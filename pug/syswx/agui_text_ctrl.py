"""A version of wx.TextCtrl that operates the pug way"""

import wx


from pug.constants import FORMAT_FLOATS
from pug.syswx.wxconstants import *
from pug.util import prettify_data

class AguiTextCtrl(wx.TextCtrl):
    """AguiTextEdit(parent, format=FORMAT_FLOATS)
    
This is a wx.TextCtrl with some special features:
    Stores the true float value, but rounds display if format is True. If 
        formatFloats is None, it looks at pug.constants.FORMAT_FLOATS 
    GetValue: 
        returns eval(TextCtrl.GetValue()), or the text if that doesn't work
        '#None#' returns None
    SetValue:
        None displays '#None#'
"""
    def __init__(self, parent, format=None):
        wx.TextCtrl.__init__(self, parent, 
                          size=wx.Size(30, WX_STANDARD_HEIGHT), 
                          style=wx.TE_PROCESS_ENTER)# | wx.TAB_TRAVERSAL)
        self.Bind(wx.EVT_NAVIGATION_KEY, self.select_all)
        self.Bind(wx.EVT_SET_FOCUS, self.select_all)  
        self.Bind(wx.EVT_TEXT_ENTER, self.select_all)      
        self.SetMinSize(wx.Size(-1, WX_STANDARD_HEIGHT))
        self.realValue = None
        self.lastValue = None
        self.format = format
        
    def select_all(self, event=None):
        wx.CallAfter(self.SelectAll)
        if event:
            event.Skip()
        
    def GetValue(self):
        if self.realValue and wx.TextCtrl.GetValue(self)==self.lastValue:
            val = self.realValue
        else:
            value = wx.TextCtrl.GetValue(self)
            try:
                val = eval(value,{},{})
            except:
                val = value
            if val == '#None#':
                # the special None string
                val = None
        return val

    def format_value(self, value):
        do_format = self.format
        if do_format is None:
            do_format = FORMAT_FLOATS
        if do_format: # float formating
            self.realValue = value
            f = prettify_data(value)
            self.lastValue = str(f)
            display = f
#            self.SetToolTipString(str(value))
        else:
            self.realValue = None
            if value is None:
                value = "#None#"
            display = str(value)
#            self.SetToolTipString(str(value))
        return display

    def ChangeValue(self, value):
        display = self.format_value(value)
        retvalue = wx.TextCtrl.ChangeValue(self, display)
        self.select_all()
        return retvalue
    
    def SetValue(self, value):
        display = self.format_value(value)
        retvalue = wx.TextCtrl.SetValue(self, display)
        return retvalue
        
                          

        