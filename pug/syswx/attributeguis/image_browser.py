"""Vector reference attribute gui"""

import os.path

import wx

from pug.syswx.pug_image_dialog import PugImageDialog
from pug.syswx.attributeguis.filename import Filename

#TODO: base this on Filename agui... only browse fn and doc are different

class ImageBrowser (Filename):
    """An attribute gui for picking an image via filename

ImageBrowser(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame. 
For other kwargs arguments, see the Base attribute GUI

Uses a browser dialog to facilitate picking a graphics file
"""        
    def browse(self, event=None):
        """browse for a new file"""
        file = self.get_control_value()
        if file:
            folder,file = os.path.split(file)
        else:
            folder = os.path.join(wx.GetApp().projectFolder,self.subfolder)
            file = None
        dlg = PugImageDialog(self.control, folder, 
                             self.aguidata.get('filter',None))
        if file:
            dlg.SetSelected(file)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            if self.fullpath:
                file = os.path.join(os.getcwd(), file)
            self.set_control_value(file)
            self.apply()
            dlg.Destroy()
