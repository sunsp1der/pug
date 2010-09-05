"""Code for pig editor mode"""
import weakref

import wx

import Opioid2D
import cOpioid2D as _c

from pig.PigState import PigState

wx = wx
Opioid2D = Opioid2D
_DEBUG = False

class EditorState(PigState):
    layers = ["__editor__",]
    selectOnUp = None
    def enter(self):
        if _DEBUG: print "EditorState.enter"
        self.interface = wx.GetApp().projectObject
        from pig.editor.GraphicsManager import graphicsManager
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
        x, y = event.pos
        node = self.scene.mouse_manager.pick_selection(x,y,
                                        wx.GetApp().selectedObjectDict)
        if node is not None:
            self.selectOnUp = weakref.ref(node)
        else:
            wx.CallAfter(self.interface.set_selection,[])
        
    def handle_mousebuttonup(self, event):
        try:
            selected = self.selectOnUp()
        except:
            pass
        else:
            x,y = selected.get_root_layer().convert_pos(*event.pos)
            if selected._cObj.Pick(_c.Vec2(x,y)):
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
        if ev.key == Opioid2D.K_u and ctrlDown:
            try:
                app = wx.GetApp()
                wx.CallAfter(app.raise_all_frames)
                wx.CallAfter(app.get_object_pugframe(
                                Opioid2D.Director.scene).pugWindow.view_source)
            except:
                pass
            
    def handle_keyup(self, ev):
        pass
                    
    def realtick(self):
        self.graphicsManager.update()    

