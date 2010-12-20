from pygame import Rect
from weakref import proxy

import wx

import Opioid2D

from pig.PigDirector import PigDirector
from pig.editor.util import get_image_path
from pig import PigSprite

wx = wx

_line_sprite_file = get_image_path("dot.png")
_handle_sprite_file = get_image_path("dot.png")
_empty_sprite_file = get_image_path("empty.png")

_HANDLE_SIZE = 6.0

class SelectBox():
    """SelectBox(): box that surrounds selected nodes
    
A selection box around a given rect. Contains dict 'lines' of line sprites whose
indexes are 'top', 'bottom', 'left', and 'right'. Also contains 'base' Sprite
which is invisible and sets the center of the object. And 'area' sprite which is
invisible and draggable.
 
Some day, this should use line primitives instead of stretched sprites. And even
handles for scaling and rotating.
"""
    rect = None
    drag_offset = (0,0)
    hotspot = None
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
        self.rect = Rect([0,0,0,0])
        self.lines = {}
        self.handles = {}
        for side in ['left','right','top','bottom']:
            # edge lines
            line = SelectBoxLineSprite()
            line.attach_to(base)
            self.lines[side] = line
            # tool handles
            handle = SelectBoxHandleSprite()
            handle.attach_to(base)
            handle.id = side
            handle.box = proxy(self)
            self.handles[side] = handle
        for corner in ['top-left','top-right','bottom-left','bottom-right']:
            handle = SelectBoxHandleSprite()
            handle.attach_to(base)
            handle.id = corner
            handle.box = proxy(self)
            self.handles[corner] = handle 
        if node:
            self.surround_node( node)
            self.start_pulse()
    
    def on_drag_begin(self):
#        layer = PigDirector.scene.get_layer("__editor1__")
        node = self.get_node()
        layer = node.layer
        position = Opioid2D.Mouse.get_position()
        world_position = layer.convert_pos(position[0], position[1])
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
        layer = PigDirector.scene.get_layer("__editor1__")
        position = Opioid2D.Mouse.get_position()
        new_position = layer.convert_pos(position[0], position[1])\
                         + self.drag_offset
        node.position = new_position 
        self.surround_node( node)
        
    def on_scale_begin(self, handle):
        node = self.get_node()  
        self.drag_from = (handle.position[0], handle.position[1])    
        self.orig_rect = node.rect.size  
        self.orig_scale = tuple(node.scale)
  
    def on_scale(self, handle):
        node = self.get_node()
        delta = (handle.position[0] - self.drag_from[0],
                 handle.position[1] - self.drag_from[1])
        location = handle.id
        if 'top' in location: 
            node.position.y += delta[0]/2.0
#            size / size + change = orig scale / new scale
#            newscale/oldscale = size+change/size
#            newscale = (size + change/size) * oldscale
            node.scale.y = self.orig_scale[1] * (self.orig_rect[1] + delta[1])\
                                                / self.orig_rect[1]
#        elif 'bottom' in location:                    
#            handle.position.y = self.lines['bottom'].position[1]\
#                                               + _HANDLE_SIZE / 2
#        if 'left' in location:
#            handle.position.x = self.lines['left'].position[0]\
#                                                - _HANDLE_SIZE / 2
#        elif 'right' in location:
#            handle.position.x = self.lines['right'].position[0]\
#                                                + _HANDLE_SIZE / 2                                                
            
        
    def start_pulse(self):
#        pulse = Opioid2D.ColorFade((0.2,0.2,0.2,1), 1.2,Opioid2D.PingPongMode)
#        
        pulse = Opioid2D.AlphaFade(0.2, 1.2, Opioid2D.PingPongMode)
        for sprite in self.lines.itervalues():
            sprite.do(pulse)
#        for sprite in self.handles.itervalues():
#            sprite.do(pulse)
            
    def __del__(self):
        self.base.delete()
        self.area.delete()
        for line in self.lines.itervalues():
            line.delete()
        for handle in self.handles.itervalues():
            handle.delete()

    def surround_node(self, node):
        try:
            hotspot = (node.image._cObj.hotspot.x, node.image._cObj.hotspot.y)
            rect = node._get_rect()
        except:
            return
        if self.rect == rect and self.hotspot == hotspot:
            return
        self.hotspot = hotspot
        self.rect = rect
        # match hotspot
        self.area.position[0] = rect.width * (0.5 - hotspot[0])
        self.area.position[1] = rect.height * (0.5 - hotspot[1])
        #match rotation
        self.base.rotation = node.rotation
        # match positions
        position = (node.position.x, node.position.y)
        self.rect.center = position
        self.base.position = position
        # match size
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
        
        for location, handle in self.handles.iteritems():
            if not handle.dragging:
                if 'top' in location: 
                    handle.position.y = self.lines['top'].position[1]\
                                                       - _HANDLE_SIZE / 2
                elif 'bottom' in location:                    
                    handle.position.y = self.lines['bottom'].position[1]\
                                                       + _HANDLE_SIZE / 2
                if 'left' in location:
                    handle.position.x = self.lines['left'].position[0]\
                                                        - _HANDLE_SIZE / 2
                elif 'right' in location:
                    handle.position.x = self.lines['right'].position[0]\
                                                        + _HANDLE_SIZE / 2                                                
        self.area.scale = (rect.width, rect.height)
        
class SelectBoxBaseSprite( PigSprite):
    layer = "__editor1__"
    auto_scene_register = False

class SelectBoxLineSprite( SelectBoxBaseSprite):
    color = (0.7,0.75,0.8,1)
    image = _line_sprite_file
    
class SelectBoxAreaSprite( SelectBoxBaseSprite):
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
        
class SelectBoxHandleSprite( SelectBoxAreaSprite):
    layer = "__editor2__"
    image = _handle_sprite_file
    draggable = True
    dragging = False
    color = (0.7,0.75,0.8,1)
    def on_create(self):
        self.scale = (_HANDLE_SIZE, _HANDLE_SIZE)
        self.state = PigDirector.scene.state.graphicsManager
        SelectBoxAreaSprite.on_create(self)

    def on_press(self):
        PigDirector.scene.state.selection_scaling = self
        self.box.on_scale_begin( self)
        
    def on_drag(self):
        self.box.on_scale( self)
        
    def on_release(self):
        PigDirector.scene.state.selection_scaling = None
