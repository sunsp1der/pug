"""Simple text entry attribute gui"""

import wx
from pug.syswx.wxconstants import *
from pug.syswx.agui_label_sizer import AguiLabelSizer
from pug.syswx.attributeguis.base import Base

# TODO: make it fold up everything beneath it

class Label (Base):
    """Label attribute GUI for demarking GUI sections. Not for attributes
    
Label(attribute, window, aguidata, **kwargs)
attribute: SPECIAL! if this value evaluates to True, it will be converted to a
    string then placed in the aguidata['label'] field. It will then be set to ''
window: the parent pugFrame
aguidata: {
    'label':<text to use>, (see attribute above)
    'font_size':<int>, 
    'background_color': wxColor, colorIDString, Hex number, or int tuple
    'indent': number of pixels to indent the label
    }
aguidata values default to the standard text look with a slightly 
darkened background...
    
# TODO:
#    'font_color': wxColor, colorIDString, Hex number, or int tuple,
#    'font_weight': wx.FONTWEIGHT_xxx constant,
#    'font_underline': bool,
#    'font_family': 
# TODO: examine some nicer ways to make fonts... FFont etc
For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        label = wx.Panel(window.get_label_window(), style=0)
        #background color
        if not hasattr(self, 'defaultBackgroundColor'):
            backgroundColor = label.GetBackgroundColour()
            r = backgroundColor[0]
            g = backgroundColor[1]
            b = backgroundColor[2]
            r -= 30
            g -= 30
            b -= 30
            if r < 0: r = 0
            if g < 0: g = 0
            if b < 0: b = 0
            backgroundColor.Set(r,g,b)
            self.__class__.defaultBackgroundColor = backgroundColor
        
        #label
        if not hasattr(self, 'defaultFontSize'):
            dummyText = wx.StaticText(label)
            defaultFont = dummyText.GetFont()
            dummyText.Destroy()
            self.__class__.defaultFontSize = defaultFont.GetPointSize()
        aguidata.setdefault('font_size', self.defaultFontSize)
        font = wx.Font(aguidata['font_size'], wx.SWISS, wx.NORMAL, 
                                wx.FONTWEIGHT_BOLD)    
        textSizer = AguiLabelSizer(parent=label, line=False, font=font)
        label.SetSizer(textSizer)
        label.textCtrl = textSizer.textCtrl
        # label.preferredWidth = textSizer.preferredWidth # FOR SASH
                            
        self.initAttribute = attribute
        aguidata['control_only'] = True        
        kwargs['aguidata'] = aguidata
        kwargs['control_widget'] = label
        Base.__init__(self, '', window, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        fontsize = aguidata.get('font_size', self.defaultFontSize)
        if fontsize != self._aguidata.get('font_size', self.defaultFontSize):
            self.__init__(attribute, window, aguidata)
            return
        if attribute:
            aguidata['label'] = attribute
        elif self.initAttribute:
            aguidata['label'] = self.initAttribute
        labelText = aguidata.get('label', '')
        self.control.textCtrl.SetLabel(labelText)
        aguidata.setdefault('background_color', self.defaultBackgroundColor)
        Base.setup(self, '', window, aguidata)
        