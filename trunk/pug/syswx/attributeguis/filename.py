"""Vector reference attribute gui"""

import os

import wx
import wx.lib.buttons as buttons

from pug.syswx.wxconstants import *
from pug.syswx.attributeguis import Base
from pug.syswx.agui_text_ctrl import AguiTextCtrl
from pug.util import prettify_path

#TODO: base imagebrowser agui on this

class Filename (Base):
    """An attribute gui for picking a filename string

Filename(attribute, window, aguidata, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame.
aguidata: {
    'subfolder': default folder added to os.getcwd(). Defaults to ''.
    'fullpath': if True, store file's absolute location. Otherwise, just store
        location data relative to os.getcwd(). Defaults to False
        }
For other kwargs arguments, see the Base attribute GUI

Uses a browser dialog to facilitate picking a graphics file
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        #attributes
        self.subfolder = aguidata.get('subfolder',"")
        self.fullpath = aguidata.get('fullpath', False)
        self.wildcards = aguidata.get('wildcards',"All files (*.*)|*.*")                        
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
        browseButton.SetToolTipString('Browse for file')
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
        cwd = os.getcwd() # save this for later
        file = self.get_control_value()
        if file:
            folder,file = os.path.split(file)
        else:
            folder = os.path.join(wx.GetApp().projectFolder, self.subfolder)
            file = ""            
        dlg = wx.FileDialog(
            self.control, 
            message="Choose a file",
            defaultDir=folder,
            defaultFile=file,
            wildcard=self.wildcards,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            if not self.fullpath:
                pre_path, short_path = os.path.split( file)
                while pre_path:
                    pre_path, slice = os.path.split(pre_path)
                    short_path = os.path.join( slice, short_path)
                    # see if pre_path is the same as cwd
                    try:
                        samefile = os.path.samefile(pre_path, cwd)
                    except AttributeError:
                        f1 = os.path.abspath(pre_path).lower()
                        f2 = os.path.abspath(cwd).lower()
                        samefile = f1 == f2                    
                    if samefile:
                        file = short_path
                        break
            self.set_control_value(file)
            self.apply()
            dlg.Destroy()
        os.chdir(cwd) # thanks for automatically changing that, windows

    def get_control_value(self):
        return self.control.value
        
    def set_control_value(self, val):
        if val:
#            val = os.path.normpath(val)
            val = prettify_path(val)
            folder,file = os.path.split(val)
            if not folder:
                folder = os.path.dirname(self.control.value)
                val = ''.join(folder,file)
        else:
            val = ""
            file = ""
        self.control.text.SetToolTipString(val)            
        self.control.text.SetValue(file)
        self.control.value = val
        