"""Code for pig editor mode"""
import weakref

import wx

import Opioid2D

from pig.PigState import PigState

_DEBUG = False

class EditorState(PigState):
    layers = ["__editor__",]
    selectOnUp = None
    def enter(self):
        if _DEBUG: print "EditorState.enter"
        self.interface = wx.GetApp().projectObject
        from pig.editor import graphicsManager
        self.graphicsManager = graphicsManager
        PigState.enter(self)
        self.graphicsManager.boxDict.clear()
        wx.CallAfter(self.graphicsManager.set_selection,
                      wx.GetApp().selectedObjectDict)
        if _DEBUG: print "EditorState.enter complete"

    def exit(self):
        if _DEBUG: print "EditorState.exit"
        self.graphicsManager.boxDict.clear()
#        wx.CallAfter(wx.GetApp().set_selection,[])
        if _DEBUG: print "EditorState.exit complete"
        PigState.exit(self)
            
    def handle_mousebuttondown(self, event):
        scene = Opioid2D.Director.scene
        x, y = event.pos
        for layer in scene.layers:
            if layer == "__editor__":
                continue
            #node = scene.get_layer(layer).pick(x,y)
            node = scene.pick(x, y, wx.GetApp().selectedObjectDict)
            if node is not None:
                self.selectOnUp = weakref.ref(node)
            else:
                wx.CallAfter(self.interface.set_selection,[])
        
    def handle_mousebuttonup(self, event):
        if self.selectOnUp and self.selectOnUp() and \
                self.selectOnUp().rect.collidepoint(event.pos):
            wx.CallAfter(self.interface.set_selection,[self.selectOnUp()])
            self.selectOnUp = None
        
    def handle_keydown(self, ev):
        # nudge keys
        nudge = 1
        shiftDown = Opioid2D.Keyboard.is_pressed(Opioid2D.K_RSHIFT) or \
                    Opioid2D.Keyboard.is_pressed(Opioid2D.K_LSHIFT)
        ctrlDown = Opioid2D.Keyboard.is_pressed(Opioid2D.K_RCTRL) or \
                    Opioid2D.Keyboard.is_pressed(Opioid2D.K_LCTRL)
        if shiftDown:
            nudge = nudge * 10
        if ctrlDown:
            nudge = nudge * 0.1            
        if ev.key == Opioid2D.K_LEFT:
            self.interface.nudge((-nudge, 0))
        if ev.key == Opioid2D.K_RIGHT:
            self.interface.nudge((nudge, 0))
        if ev.key == Opioid2D.K_UP:
            self.interface.nudge((0, -nudge))
        if ev.key == Opioid2D.K_DOWN:
            self.interface.nudge((0, nudge))
        if ev.key == Opioid2D.K_DELETE:
            selectedDict = list(wx.GetApp().selectedObjectDict)
            for item in selectedDict:
                if isinstance(item, Opioid2D.public.Node.Node):
                    if _DEBUG: print 'callafter'
                    wx.CallAfter(item.delete)
        if ev.key == Opioid2D.K_s and ctrlDown:
            wx.CallAfter(self.interface.save_using_working_scene)
        if ev.key == Opioid2D.K_q and ctrlDown:
            wx.CallAfter(self.interface.quit)
        if ev.key == Opioid2D.K_w and ctrlDown:
            wx.CallAfter(wx.GetApp().raise_all_frames)
            
    def handle_quit(self, ev):
        wx.CallAfter(wx.GetApp()._evt_project_frame_close)
        
    def realtick(self):
        self.graphicsManager.update()    
