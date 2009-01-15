"""Layer attribute gui... a list of layers with control buttons on right"""

import wx

from pug.syswx.attributeguis import ListEdit
from pug.syswx.wxconstants import WX_STANDARD_HEIGHT

class SceneLayers (ListEdit):
    """An attribute gui that shows a list of layers and has control buttons

Layer(attribute, window, aguidata, **kwargs)
aguidata: possible entries-
    see ListEdit
attribute: what attribute of window.object is being controlled
window: the parent window. 
For other kwargs arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata, **kwargs):
        # control
        aguidata.setdefault('label','   layers')
        aguidata.setdefault('height', WX_STANDARD_HEIGHT * 3)
        aguidata.setdefault('add',[self.evt_add_button, 'Add a layer'])
        aguidata.setdefault('delete',[self.evt_delete_button, 
                                      'Delete selected layer'])
        infotext = '\n'.join(
                ["Scene layers\n",
                 "To rearrange the order of layers, you must edit the",
                 "layers attribute in this scene's file."])
        aguidata.setdefault('info', 
                            [infotext, 'Info about using Opioid2D layers'])
        aguidata.setdefault('label','   layers')                        
        ListEdit.__init__(self, attribute, window, aguidata, **kwargs)
        
        
    def evt_add_button(self, event=None):
        dlg = wx.TextEntryDialog( self.control, 
                                  "Enter the new layer's name", 
                                  "New Layer")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            name.strip()
            if name:
                self._window.object.add_layer(str(name))
                self.refresh()
        dlg.Destroy()

    def evt_delete_button(self, event=None):
        dlg = wx.MessageDialog(self.control,
                    '\n'.join(['Deleting layer will delete all',
                               'nodes on the layer. Continue?']),
                           'Confirm Delete', wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_YES:
            layer = self.listbox.GetStringSelection()
            if layer:
                self._window.object.delete_layer(str(layer))
            self.refresh()
        dlg.Destroy()
        
    def get_control_value(self):
        return self.list
    
    def set_control_value(self, value):
        self.list = value
        value.reverse()
        self.listbox.Set(value)
        