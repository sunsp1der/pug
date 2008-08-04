"""A version of wx.TextCtrl that operates the pug way"""

import wx

from pug.syswx.wxconstants import *

# TODO: deals with tab stuff
# TODO: applies when losing focus
# TODO: doesn't apply when has focus
# TODO: select all on get focus

class AguiTextCtrl(wx.TextCtrl):
    """AguiTextEdit(parent, Id=-1)
    
This is a wx.TextCtrl with some special features:
    GetValue: 
        returns eval(TextCtrl.GetValue()), or the text if that doesn't work
        '#None#' returns None
    SetValue:
        None displays '#None#'
"""
    def __init__(self, parent, Id=-1):
        wx.TextCtrl.__init__(self, parent, Id, 
                          size=wx.Size(30, WX_STANDARD_HEIGHT), 
                          style=wx.TE_PROCESS_ENTER)
        self.SetMinSize(wx.Size(0, WX_STANDARD_HEIGHT))
        
    def GetValue(self):
        value = wx.TextCtrl.GetValue(self)
#        if value == 'None' and last_value() == 'None':
            # let the user keep 'None' as a string IF it started out that way
#            return 'None'
        try:
            val = eval(value,{},{})
        except:
            val = value
        if val == '#None#':
            # the special None string
            val = None
        return val
    
    def SetValue(self, value):
        if value is None:
            value = "#None#"
        retvalue = wx.TextCtrl.SetValue(self, str(value))
        wx.CallAfter(self.SetInsertionPointEnd)
        return retvalue
        
                          

        