"""Vector reference attribute gui"""

import os.path

import wx

import pygame

from pug.syswx.pug_image_dialog import PugImageDialog
from pug.syswx.attributeguis.filename import Filename

#TODO: base this on Filename agui... only browse fn and doc are different

class PigImageBrowser (Filename):
    """An attribute gui for picking a Sprite image via filename

ImageBrowser(attribute, window, **kwargs)
attribute: what attribute of window.object is being controlled
window: the parent pugFrame. 
For other kwargs arguments, see the Base attribute GUI

Uses a browser dialog to facilitate picking a graphics file
"""        
    checkbox = None
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
        try:
            original_size = self.window.object.rect.size
            scale = self.window.object.scale
        except:
            pass
        else:
            checkbox = wx.CheckBox( dlg, 
                                label="Adjust scale to maintain sprite size")
            checkbox.SetValue(True)
            sizer = dlg.GetSizer()
            sizer.Insert(len(sizer.GetChildren())-1, checkbox, 0, wx.ALL, 
                         border=5)
            self.checkbox = checkbox
        if file:
            dlg.SetSelected(file)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetFile()
            if self.fullpath:
                file = os.path.join(os.getcwd(), file)
            self.set_control_value(file)
            self.apply()
            dlg.Destroy()
            
    def set_control_value( self, val, adjust_scale=False):
        try:
            if adjust_scale or (self.checkbox and self.checkbox.GetValue()):
                # do scale adjust
                original_rect = self.window.object.rect.size
                scale = self.window.object.scale
                image = pygame.image.load( val)
                new_size = image.get_size()
                new_scale = (float(original_rect[0]) / new_size[0],
                             float(original_rect[1]) / new_size[1])
                self.window.object.scale = new_scale
        except:
            pass
#            from pug.syswx.util import show_exception_dialog
#            show_exception_dialog()                
        Filename.set_control_value(self,val)
