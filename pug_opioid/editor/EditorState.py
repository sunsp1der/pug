"""Code for pug_opioid editor mode"""

import wx
import Opioid2D

class EditorState(Opioid2D.State):
    layers = ["__selections__",]
    def enter(self):
        self.interface = wx.GetApp().projectObject
        from pug_opioid.editor import selectionManager
        self.selectionManager = selectionManager
        selectionManager.set_selection( wx.GetApp().selectedRefSet)

    def exit(self):
        self.selectionManager.set_selection([])
    
    def handle_mousebuttondown(self, event):
        scene = Opioid2D.Director.scene
        x, y = event.pos
        for layer in scene.layers:
            if layer == "__selections__":
                continue
            node = scene.get_layer(layer).pick(x,y)
            if node is not None:
                wx.CallAfter(self.interface.set_selection,[node])
                return
        wx.CallAfter(self.interface.set_selection,[])
        
    def handle_keydown(self, ev):
        # nudge keys
        nudge = 1
        if Opioid2D.Keyboard.is_pressed(Opioid2D.K_RSHIFT) or \
                    Opioid2D.Keyboard.is_pressed(Opioid2D.K_LSHIFT):
            nudge = nudge * 10
        if Opioid2D.Keyboard.is_pressed(Opioid2D.K_RCTRL) or \
                    Opioid2D.Keyboard.is_pressed(Opioid2D.K_LCTRL):
            nudge = nudge * 0.1            
        if ev.key == Opioid2D.K_LEFT:
            self.interface.nudge((-nudge, 0))
        if ev.key == Opioid2D.K_RIGHT:
            self.interface.nudge((nudge, 0))
        if ev.key == Opioid2D.K_UP:
            self.interface.nudge((0, -nudge))
        if ev.key == Opioid2D.K_DOWN:
            self.interface.nudge((0, nudge))
        
    def realtick(self):
        self.selectionManager.update_boxes()
    