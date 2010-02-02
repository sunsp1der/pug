"""Vector reference attribute gui"""

import os.path

import wx
import wx.lib.buttons as buttons

from pug.syswx.wxconstants import *
from pug.syswx.attributeguis import Base
from pug.syswx.pugbutton import PugButton
from pug.syswx.agui_text_ctrl import AguiTextCtrl
from pug.syswx.pug_image_dialog import PugImageDialog

class ImageBrowser (Base):
    """An attribute gui for picking an image via filename

ImageBrowser(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame. 
For other kwargs arguments, see the Base attribute GUI

Uses a browser dialog to facilitate picking a graphics file
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        #attributes
                         
        SPACING = 4 # for button
        
        # control
        control = wx.Panel(window, size=(1,WX_STANDARD_HEIGHT))
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        control.value = ''
        text = AguiTextCtrl(control)
        text.SetEditable(False)
        control.text = text
        browseBmp = wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_TOOLBAR,
                                              WX_BUTTON_BMP_SIZE)
        browseButton = buttons.ThemedGenBitmapButton(control, bitmap=browseBmp, 
                                       size=WX_BUTTON_SIZE)
        browseButton.SetToolTipString('Browse')
        browseButton.Bind(wx.EVT_BUTTON, self.browse, browseButton)

        controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        control.SetSizer(controlSizer)
        controlSizer.Add(browseButton,0)
        controlSizer.Add(text,1,wx.EXPAND | wx.WEST, SPACING)
#        controlSizer.AddMany([(textSizer,1,wx.EXPAND | wx.EAST, SPACING),
#                              (browseButton,0)])
#        control.SetSize(controlSizer.MinSize)
#        control.SetMinSize((-1,controlSizer.MinSize[1]))
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def browse(self, event=None):
        """browse for a new file"""
        file = self.get_control_value()
        if file:
            folder,file = os.path.split(file)
        else:
            folder = wx.GetApp().projectFolder
            file = None
        dlg = PugImageDialog(self.control, folder)
        if file:
            dlg.SetSelected(file)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            self.set_control_value(file)
            self.apply()
            dlg.Destroy()

    def get_control_value(self):
        return self.control.value
        
    def set_control_value(self, val):
        folder,file = os.path.split(val)
        if not folder:
            folder = os.path.dirname(self.control.value)
            val = ''.join(folder,file)
        self.control.text.SetToolTipString(val)            
        self.control.text.SetValue(file)
        self.control.value = val
        