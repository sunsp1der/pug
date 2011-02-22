"""Layer attribute gui... a list of layers with control buttons on right"""
from functools import partial

import wx

from pug.syswx.attributeguis import ListEdit
from pug.syswx.wxconstants import WX_STANDARD_HEIGHT

from pig.editor.util import undoable_delete_layer

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
        aguidata.setdefault('arrange_up',[self.evt_arrange_up_button])
        aguidata.setdefault('arrange_down',[self.evt_arrange_down_button])
#        infotext = '\n'.join(
#                ["Scene layers\n",
#                 "To rearrange the order of layers, you must edit the",
#                 "layers attribute in this scene's file."])
#        aguidata.setdefault('info', 
#                            [infotext, 'Info about using Opioid2D layers'])
        aguidata.setdefault('label','   layers')                        
        ListEdit.__init__(self, attribute, window, aguidata, **kwargs)
        
    def evt_add_button(self, event=None):
        dlg = wx.TextEntryDialog( self.control, 
                                  "Enter the new layer's name", 
                                  "New Layer")
        if dlg.ShowModal() == wx.ID_OK:
            name = str(dlg.GetValue())
            name.strip()
            if name and self.listbox.FindString(name) == wx.NOT_FOUND:
                do_fn = partial(self.do_add, name)
                undo_fn = partial(self.window.object.delete_layer, name)
                do_fn()
                wx.GetApp().history.add("Add layer", undo_fn, do_fn)
        dlg.Destroy()
        
    def do_add(self, name):
        self.window.object.add_layer(name)
        self.refresh()
        self.listbox.Select(self.listbox.FindString(name))

    def evt_delete_button(self, event=None):
        if not self.listbox.GetStringSelection():
            return
        layer = self.listbox.GetStringSelection()
        undoable_delete_layer(str(layer))
        self.refresh()
        
    def evt_arrange_up_button(self, event=None):
        self.arrange(1)
        
    def evt_arrange_down_button(self, event=None):
        self.arrange(-1)
        
    def arrange(self, delta):
        selected = self.listbox.GetStringSelection()
        if not selected:
            return
        layerlist = self.get_attribute_value()
        try:
            i = layerlist.index(selected)
        except:
            return
        if i + delta < 0:
            delta = -i
        elif i + delta >= len(layerlist):
            delta = len(layerlist) - i - 1
        if delta == 0:
            return
        do_fn = partial(self.do_arrange, selected, delta)
        undo_fn = partial(self.do_arrange, selected, -delta)
        do_fn()
        wx.GetApp().history.add("Move layer",undo_fn, do_fn)
        
    def do_arrange(self, layer, delta):
        self.window.object.move_layer( layer, delta)
        i = self.listbox.FindString(layer)
        self.listbox.Select(i)
        self.window.object.nodes.doCallbacks() # let guis know nodes changed
        self.refresh()

    def get_control_value(self):
        retval = self.list[:]
        retval.reverse()
        return retval
    
    def set_control_value(self, value):
        selected = self.listbox.GetStringSelection()
        self.list = value
        value.reverse()
        self.listbox.Set(value)
        self.listbox.Select(self.listbox.FindString(selected))