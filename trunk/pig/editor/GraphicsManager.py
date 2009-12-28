"""Manages drawing and maintaining selections"""

import os.path

import wx
import Opioid2D
from Opioid2D import Mouse
from pug.CallbackWeakKeyDictionary import CallbackWeakKeyDictionary

from pig.editor import selection_helpers

_DEBUG = False

class GraphicsManager():
    """GraphicsManager()

Object that manages editor graphics in the Opioid2D frame
"""
    new_selection = None
    def __init__(self):
        self.boxDict = CallbackWeakKeyDictionary()
    
    def on_set_selection(self, selectedObjectDict):
        """on_set_selection( selectedObjectDict)
        
Callback from pug.App...
"""
        if _DEBUG: print 'GraphicsManager.on_set_selection',\
                            selectedObjectDict.data
        self.set_selection( selectedObjectDict)
        
    def set_selection(self, selectedObjectDict):
        """set_selection( selectedObjectDict)
        
Set the selection to the given list of objects. Draw a box around each one.
This action will be deferred until after current update...
"""
        if _DEBUG: print 'GraphicsManager.set_selection', \
                            selectedObjectDict.data
        self.new_selection = selectedObjectDict

    def do_set_selection(self,  selectedObjectDict):
        """do_set_selection( selectedObjectDict)
        
Set the selection to the given list of objects. Draw a box around each one.
"""
        if _DEBUG: print 'GraphicsManager.do_set_selection', \
                            selectedObjectDict.data
        keySet = set(self.boxDict.keys())
        selectSet = set()
        for ref in selectedObjectDict.itervalues():
            selectSet.add(ref())
        deselectSet = keySet.difference(selectSet)
        for deselect in deselectSet:
            if _DEBUG: print '   deselect', deselect
            self.boxDict.pop(deselect)
        selectSet.difference_update(keySet)
        for item in selectSet:
            if _DEBUG: print '   create SelectBox', item
            if not hasattr(item, 'rect'):
                if _DEBUG: print '      NO RECT!', item
                continue
            self.boxDict[item] = selection_helpers.SelectBox(item)
    
    def update(self):
        if self.new_selection is not None:
            if _DEBUG: print "GraphicsManager.update():",self.new_selection.data
            # don't do anything if we're in the middle of a drag
            for box in self.boxDict.itervalues():
                if box.area.dragging:
                    return
            new_selection = self.new_selection
            self.new_selection = None
            self.do_set_selection(new_selection)
            if _DEBUG: print "   GraphicsManager.update() DONE"
        self.update_selection_boxes()
        
    def update_selection_boxes(self):
        """update_selection_boxes()
        
update all selection boxes. 
"""
#This whole thing is in a try clause because of sync issues.
        try:
            for node, box in self.boxDict.iteritems():
                # try to remove deleted items
                if getattr(node,'deleted',True):
                    self.boxDict.pop(node)
                    # messed with the dict, so start over
                    self.update_selection_boxes()
                    break
                rect = node.get_rect()
                if box.area.dragging:
                    if box.rect != box.area.rect:
                        layer = Opioid2D.Director.scene.get_layer(
                                                            "__editor__")
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
            if _DEBUG: 
                import sys
                print "GraphicsManager.update_selection_boxes: exception"
                print sys.exc_info()[1]
            pass
            
graphicsManager = GraphicsManager()
# interface with selection_helpers
selection_helpers.theGraphicsManager = graphicsManager 
