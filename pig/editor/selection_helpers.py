from pygame import Rect
from weakref import proxy

import wx

import Opioid2D

from pig.PigDirector import PigDirector
from pig.editor.util import get_image_path
from pig import PigSprite

wx = wx

_line_sprite_file = get_image_path("dot.png")
_empty_sprite_file = get_image_path("empty.png")

class SelectBox():
    """SelectBox()
    
A selection box around a given rect. Contains dict 'lines' of line sprites whose
indexes are 'top', 'bottom', 'left', and 'right'. Also contains 'base' Sprite
which is invisible and sets the center of the object. And 'area' sprite which is
invisible and draggable.
 
Some day, this should use line primitives instead of stretched sprites. And even
handles for scaling and rotating.
"""
    rect = None
    drag_offset = (0,0)
    def __init__(self, node = None):
        """__init__( node=None)

node: any object containing a 'rect' attribute that is a pygame rect
"""
        self.graphicsManager = PigDirector.scene.state.graphicsManager
        base = SelectBoxBaseSprite() 
        area = SelectBoxAreaSprite()
        area.attach_to(base)
        area.position = (0,0)        
        self.base = base
        self.area = area
        self.area.box = proxy(self)
        self.lines = {}
        self.rect = Rect([0,0,0,0])
        for side in ['left','right','top','bottom']:
            line = SelectBoxLineSprite()
            line.attach_to(base)
            self.lines[side] = line
        if node:
            self.surround_node( node)
            self.start_pulse()
    
    def on_drag_begin(self):
        layer = PigDirector.scene.get_layer("__editor__")
        position = Opioid2D.Mouse.get_position()
        world_position = layer.convert_pos(position[0], position[1])
        node = self.get_node()
        if node:
            self.drag_offset = node.position - world_position
        else:
            self.drag_offset = (0,0)   
        
    def get_node(self):  
        boxDict = self.graphicsManager.boxDict
        for node,box in boxDict.iteritems():
            if box == self:
                return node
        
    def on_drag(self, node):
        layer = PigDirector.scene.get_layer("__editor__")
        position = Opioid2D.Mouse.get_position()
        new_position = layer.convert_pos(position[0], position[1])\
                         + self.drag_offset
        node.position = new_position 
        self.surround_node( node)
        
    def start_pulse(self):
        pulse = Opioid2D.AlphaFade(0.6, 1.5, Opioid2D.PingPongMode)
        for sprite in self.lines.itervalues():
            sprite.do(pulse)
            
    def __del__(self):
        self.base.delete()
        self.area.delete()
        for line in self.lines.itervalues():
            line.delete()

    def surround_node(self, node):
        try:
            hotspot = (node.image._cObj.hotspot.x, node.image._cObj.hotspot.y)
            rect = node._get_rect()
        except:
            return
        self.area.position[0] = rect.width * (0.5 - hotspot[0])
        self.area.position[1] = rect.height * (0.5 - hotspot[1])
        self.base.rotation = node.rotation
        
        position = (node.position.x, node.position.y)
        #position = (rect.center[0]+0.5, rect.center[1]+0.5)
        self.rect.center = position
        self.base.position = position
        if self.rect == rect:
            return
        elif self.rect.size != rect.size:
            line = self.lines['left']
            line.position = self.area.position + (rect.width * -0.5 - 1, 0.5)
            line.scale = (1,rect.height+2)
            
            line = self.lines['right']
            line.position = self.area.position + (rect.width * 0.5 + 1, 0.5)
            line.scale = (1,rect.height+2)
            
            line = self.lines['top']
            line.position = self.area.position + (0, rect.height * -0.5 - 1)
            line.scale = (rect.width + 3, 1)
            
            line = self.lines['bottom']
            line.position = self.area.position + (0, rect.height * 0.5 + 1)
            line.scale = (rect.width + 1, 1)
            self.rect.size = rect.size
            self.area.scale = (rect.width, rect.height)
        
class SelectBoxBaseSprite( PigSprite):
    layer = "__editor__"
    auto_scene_register = False

class SelectBoxLineSprite( SelectBoxBaseSprite):
    image = _line_sprite_file
    
class SelectBoxAreaSprite( SelectBoxLineSprite):
    #image = _line_sprite_file; alpha = 0.5 # visible for testing
    image = _empty_sprite_file
    draggable = True
    dragging = False
    def on_create(self):
        self.graphicsManager = PigDirector.scene.state.graphicsManager
        self.mouse_register("single")
        
    def on_drag_begin(self):
        self.box.on_drag_begin()
        PigDirector.scene.state.selectOnUp = None
        self.dragging = True

    def on_drag_end(self):
        self.dragging = False
        PigDirector.scene.state.selectOnUp = None
        self.graphicsManager.update_selection_boxes()
        wx.CallAfter(wx.GetApp().selection_refresh)
