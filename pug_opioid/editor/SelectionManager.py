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
    new_selection = None
    def __init__(self):
        self.boxDict = CallbackWeakKeyDictionary()
    
    def on_set_selection(self, selectedRefSet):
        """on_set_selection( selectedRefSet)
        
Callback from pug.App...
"""
        self.set_selection( selectedRefSet)
        
    def set_selection(self, selectedRefSet):
        """set_selection( selectedRefSet)
        
Set the selection to the given list of objects. Draw a box around each one.
This action will be deferred until after current update...
"""
        if not isinstance(selectedRefSet, set):
            selectedRefSet = set(selectedRefSet)
        self.new_selection = selectedRefSet

    def do_set_selection(self,  selectedRefSet):
        """do_set_selection( selectedRefSet)
        
Set the selection to the given list of objects. Draw a box around each one.
"""
        keySet = set(self.boxDict.keys())
        selectSet = set()
        for ref in selectedRefSet:
            selectSet.add(ref())
        deselectSet = keySet.difference(selectSet)
        for deselect in deselectSet:
            self.boxDict.pop(deselect)
        selectSet.difference_update(keySet)
        for item in selectSet:
            if not hasattr(item, 'rect'):
                continue
            self.boxDict[item] = SelectBox(item)
    
    def update(self):
        if self.new_selection is not None:
        # don't do anything if we're in the middle of a drag
            new_selection = self.new_selection
            self.new_selection = None
            for box in self.boxDict.itervalues():
                if box.area.dragging:
                    return
            self.do_set_selection(new_selection)
        self.update_boxes()
        
    def update_boxes(self):
        """update_boxes()
        
update all selection boxes. 
"""
#This whole thing is in a try clause because of sync issues.
        try:
            for node, box in self.boxDict.iteritems():
                # try to remove deleted items
                if getattr(node,'deleted',True):
                    self.boxDict.pop(node)
                    # messed with the dict, so start over
                    self.update_boxes()
                    break
                rect = node.get_rect()
                if box.area.dragging:
                    if box.rect != box.area.rect:
                        layer = Opioid2D.Director.scene.get_layer(
                                                            "__selections__")
                        position = Mouse.get_position()
                        world_position = layer.convert_pos(position[0], 
                                                           position[1])
                        box.area.position = (0,0)
                        node.position = world_position
                        box.set_position(world_position)
                else:
                    if box.rect != rect:
                        box.surround_node( node)
            return
        except:
            pass
            
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
            self.surround_node( node)
            
    def __del__(self):
        self.base.delete()
        self.area.delete()
        for line in self.lines.itervalues():
            line.delete()

    def surround_node(self, node):
        rect = node.rect
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
        self.base.rotation = node.rotation

    def set_position(self, position):
        self.rect.center = position
        self.base.position = position
        
class SelectBoxLineSprite( Opioid2D.gui.GUISprite):
    image = _line_sprite_file
    layer = "__selections__"

class SelectBoxBaseSprite( Opioid2D.Sprite):
    layer = "__selections__"
    
class SelectBoxAreaSprite( Opioid2D.gui.GUISprite):
    image = _empty_sprite_file
    layer = "__selections__"
    draggable = True
    dragging = False
    
    def on_drag_begin(self):
        Opioid2D.Director.scene.state.selectOnUp = None
        self.dragging = True

    def on_drag_end(self):
        Opioid2D.Director.scene.state.selectOnUp = None
        selectionManager.update_boxes()
        wx.CallAfter(wx.GetApp().selection_refresh)
        self.dragging = False