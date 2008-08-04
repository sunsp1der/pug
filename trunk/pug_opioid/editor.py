"""Code for pug_opioid editor mode"""

import wx
import Opioid2D

class EditorState(Opioid2D.State):
    def enter(self):
        layers = ["selections",]
        self.interface = wx.GetApp().projectObject
    
    def handle_mousebuttondown(self, event):
        x, y = ev.pos
        for layer in Opioid2D.scene.layers:
            if layer.name == "selections":
                continue
            node = layer.pick(x,y)
            if node is not None:
                self.set_selection([node])
                return
        self.clear_selection()

    def set_selection(self, nodeList):
        self.interface.set_selection(nodeList)    
    
    def clear_selection(self):
        pass
    