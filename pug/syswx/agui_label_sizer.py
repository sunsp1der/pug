import wx

from pug.syswx.wxconstants import *

class AguiLabelSizer(wx.BoxSizer):
    """AguiLabelSizer(parent, label='', line=True, font=None)

parent: the parent window
label: the text to display
line: if True, create a line at the bottom of the sizer
font: a font object to be used for the font... defaults to default font
    
A sizer that contains properly formatted text for attribute guis

Includes a spacer to lower text WX_TEXTEDIT_LABEL_YOFFSET pixels, the static
text object, which is stored in AguiLabelSizer.text, and a wx.line control, 
which is stored in AguiLabelSizer.line, to visually separate text from text on 
next line.
"""
    
    def __init__(self, parent, label='', line = True, flag=0, font=None):
        wx.BoxSizer.__init__(self, orient=wx.VERTICAL)
        text = wx.StaticText(parent, label=label)
        if font:
            text.SetFont(font)
        text.SetMinSize((-1,-1))     
        self.AddSpacer((1, WX_TEXTEDIT_LABEL_YOFFSET))
        textSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        textSizer.Add(text, 1, wx.EXPAND | wx.WEST, 2)
        self.AddSizer(textSizer, 1)
        if line:
            line = wx.StaticLine(parent=parent, style = 0)            
            self.Add(line, flag=wx.EXPAND)
            self.line = line        
        self.textCtrl = text
        # FOR SASH
        # self.preferredWidth = self.MinSize[0]
        
    def SetLabel(self, text=''):
        self.textCtrl.Label = text
