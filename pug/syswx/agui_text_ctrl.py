"""A version of wx.TextCtrl that operates the pug way"""

import wx
wx=wx

from pug.constants import FORMAT_FLOATS
from pug.syswx.wxconstants import *

# TODO: deals with tab stuff
# TODO: doesn't apply when has focus
# TODO: select all on get focus

class AguiTextCtrl(wx.TextCtrl):
    """AguiTextEdit(parent, formatFloats=None)
    
This is a wx.TextCtrl with some special features:
    Stores the true float value, but rounds display if formatFloats is True. If 
        formatFloats is None, it looks at pug.constants.FORMAT_FLOATS 
    GetValue: 
        returns eval(TextCtrl.GetValue()), or the text if that doesn't work
        '#None#' returns None
    SetValue:
        None displays '#None#'
"""
    def __init__(self, parent, formatFloats=None):
        wx.TextCtrl.__init__(self, parent, 
                          size=wx.Size(30, WX_STANDARD_HEIGHT), 
                          style=wx.TE_PROCESS_ENTER)# | wx.TAB_TRAVERSAL)
        self.Bind(wx.EVT_NAVIGATION_KEY, self.select_all)
        self.Bind(wx.EVT_SET_FOCUS, self.select_all)  
        self.Bind(wx.EVT_TEXT_ENTER, self.select_all) # doesn't work !?     
        self.SetMinSize(wx.Size(-1, WX_STANDARD_HEIGHT))
        self.floatValue = None
        self.lastValue = None
        self.formatFloats = formatFloats
        
    def select_all(self, event=None):
        wx.CallAfter(self.SelectAll)
        if event:
            event.Skip()
        
    def GetValue(self):
        if self.floatValue and wx.TextCtrl.GetValue(self)==self.lastValue:
            val = self.floatValue
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
        do_format = self.formatFloats
        if do_format is None:
            do_format = FORMAT_FLOATS
        if type(value) == float and do_format: # float formating
            self.floatValue = value
            f = "%.3f" % value
            if f[-2:] == '00':
                f = f[:-2]
            elif f[-1:] == '0':
                f = f[:-1]
            self.lastValue = str(f)
            display = f
#            self.SetToolTipString(str(value))
        else:
            self.floatValue = None
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
        
                          

        