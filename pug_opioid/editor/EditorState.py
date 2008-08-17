"""Code for pug_opioid editor mode"""

import wx
import Opioid2D

class EditorState(Opioid2D.State):
    layers = ["selections",]
    def enter(self):
        self.interface = wx.GetApp().projectObject
        from pug_opioid.editor import selectionManager
        self.selectionManager = selectionManager
    
    def handle_mousebuttondown(self, event):
        scene = Opioid2D.Director.scene
        x, y = event.pos
        for layer in scene.layers:
            if layer == "selections":
                continue
            node = scene.get_layer(layer).pick(x,y)
            if node is not None:
                wx.CallAfter(self.interface.set_selection,[node])
                return
        wx.CallAfter(self.interface.set_selection,[])
        
    def realtick(self):
        self.selectionManager.update_boxes()

    