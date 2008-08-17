"""Manages drawing and maintaining selections"""

import os.path

import wx
import Opioid2D
from Opioid2D import Mouse
from pygame import Rect

from pug.util import CallbackWeakKeyDictionary

_line_sprite_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 "Images/dot.png")
_empty_sprite_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 "Images/empty.png")

class SelectionManager():
    """SelectionManager()

Object that manages selection graphics in the Opioid2D frame
"""
    def __init__(self):
        self.boxDict = CallbackWeakKeyDictionary()
    
    def on_set_selection(self, selectRefSet):
        """on_set_selection( selectRefSet)
        
Set the selection to the given list of objects. Draw a box around each one.
"""
        keySet = set(self.boxDict.keys())
        selectSet = set()
        for ref in selectRefSet:
            selectSet.add(ref())
        deselectSet = keySet.difference(selectSet)
        for deselect in deselectSet:
            self.boxDict.pop(deselect)
        selectSet.difference_update(keySet)
        for item in selectSet:
            if not hasattr(item, 'rect'):
                continue
            self.boxDict[item] = SelectBox(item)
    
    def update_boxes(self):
        for node, box in self.boxDict.iteritems():
            rect = node.get_rect()
            if box.area.dragging:
                if box.rect != box.area.rect:
                    layer = Opioid2D.Director.scene.get_layer("selections")
                    position = Mouse.get_position()
                    world_position = layer.convert_pos(position[0], position[1])
                    box.area.position = (0,0)
                    node.position = world_position
                    box.set_position(world_position)
            else:
                if box.rect != rect:
                    box.set_rect( rect)
            
selectionManager = SelectionManager()
        
class SelectBox():
    """SelectBox()
    
A selection box around a given rect. Contains dict 'lines' of line sprites whose
indexes are 'top', 'bottom', 'left', and 'right'. Also contains 'base' Sprite
which is invisible and sets the center of the object.
 
Some day, this should use line primitives instead of stretched sprites.
"""
    rect = None
    def __init__(self, node = None):
        """__init__( node=None)

node: any object containing a 'rect' attribute that is a pygame rect
"""
        base = SelectBoxBaseSprite() 
        area = SelectBoxAreaSprite()
        area.attach_to(base)
        area.position = (0,0)        
        self.base = base
        self.area = area
        self.lines = {}
        self.rect = Rect([0,0,0,0])
        for side in ['left','right','top','bottom']:
            line = SelectBoxLineSprite()
            line.attach_to(base)
            self.lines[side] = line
        if node:
            self.set_rect( node.rect)
            
    def __del__(self):
        self.base.delete()
        self.area.delete()
        for line in self.lines.itervalues():
            line.delete()

    def set_rect(self, rect=None):
        if self.rect == rect:
            return
        elif self.rect.size != rect.size:
            line = self.lines['left']
            line.position = (rect.width * -0.5, 0)
            line.scale = (1,rect.height)
            
            line = self.lines['right']
            line.position = (rect.width * 0.5, 0)
            line.scale = (1,rect.height)
            
            line = self.lines['top']
            line.position = (0, rect.height * -0.5)
            line.scale = (rect.width - 1, 1)
            
            line = self.lines['bottom']
            line.position = (0, rect.height * 0.5)
            line.scale = (rect.width + 1, 1)
            self.rect.size = rect.size
            self.area.scale = (rect.width, rect.height)
        self.set_position(rect.center)

    def set_position(self, position):
        self.rect.center = position
        self.base.position = position
        
class SelectBoxLineSprite( Opioid2D.gui.GUISprite):
    image = _line_sprite_file
    layer = "selections"

class SelectBoxBaseSprite( Opioid2D.Sprite):
    layer = "selections"
    
class SelectBoxAreaSprite( Opioid2D.gui.GUISprite):
    image = _empty_sprite_file
    layer = "selections"
    draggable = True
    dragging = False
    
    def on_drag_begin(self):
        self.dragging = True

    def on_drag_end(self):
        selectionManager.update_boxes()
        self.dragging = False
