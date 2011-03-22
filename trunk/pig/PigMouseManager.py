from Opioid2D.public.gui.GUIManager import Drag
from Opioid2D.public.Mouse import Mouse
from Opioid2D.internal.objectmgr import ObjectManager
from Opioid2D import Delay, CallFunc
import cOpioid2D as _c

from PigDirector import PigDirector
import pygame

PigDirector = PigDirector

class PigMouseManager():
    """PigMouseManager(): Manages mouse events for objects in a scene.
    
Access this object through scene.mouse_manager. To register an object for mouse 
events, use Sprite.mouse_register(). 
"""
    def __init__(self):
        self._multi_objects = set() # all nodes registered as 'multi'
        self._click_objects = set() # all nodes registered as 'click'
        self._single_objects = set() # all nodes registered 
        self._under = []
        self._drag = None
        self._clicking = []
        self._pos_dict = {} 

    def register(self, object, type="single"):
        """register( object, type="single")
        
object: the sprite to register for mouse events
type: "single", "multi", or "click". Gui objects check all mouse events. If one is
under the mouse, no other mouse events will be checked. Game objects check all
mouse events, but if one is found others are still checked. Click objects only
check for mouse down and mouse up events. 

Registering can upgrade type from "multi" to "single" or from "click" to "multi" or 
"single". It will NOT downgrade type. To downgrade, you must unregister then re-
register at the lower callback level.
"""
        if type not in ['single', 'multi', 'click']:
            raise ValueError("Must register for mouse events as"+\
                             " 'single', 'multi', or 'click'")
        if (type == "multi" and object._mouse_registered == "single") or \
                (type == "click" and (object._mouse_registered == "single" or \
                                      object._mouse_registered == "multi")):
            # we're already getting those events
            return   
        if type == "single":
            group = self._single_objects
        elif type == "multi":
            group = self._multi_objects
        elif type == "click":
            group = self._click_objects
        (Delay(0) + CallFunc(group.add, object)).do()
        object._mouse_registered = type
            
    def unregister(self, object):
        """unregister( object): unregister object from mouse events"""
        try:
            self._click_objects.remove(object)
        except KeyError:
            try:
                self._multi_objects.remove(object)
            except KeyError:
                self._single_objects.discard(object)
                
    def get_relative_pos(self, layer):
        if not layer:
            return None
        try:
            return self._pos_dict[layer]
        except:
            pos = layer.convert_pos(*self._pos_dict['root'])
            self._pos_dict[layer] = pos
            return pos
                
    def tick(self, evs=None):
        mx,my = Mouse.get_position()
        self._pos_dict = {'root':(mx,my)}
        scene = PigDirector.get_scene()
        results = []
        i = 0
        for e in self._single_objects:
            l = e.get_root_layer()
            if not l:
                continue
            wx,wy = self.get_relative_pos(l)
            p = e._cObj.Pick(_c.Vec2(wx,wy))
            p = ObjectManager.c2py(p)
            if self._drag and self._drag._object is p:
                continue
            if p and p in self._single_objects:
                idx = scene.layers.index(l.get_name())
                results.append((idx,i,p))
                i += 1
        if results:
            results.sort()
            under = [results[-1][2]]
#            under[0].on_hover()
        else:
            under = []
            for e in self._multi_objects:
                l = e.get_root_layer()
                if not l:
                    continue
                wx,wy = self.get_relative_pos(l)
                p = e._cObj.Pick(_c.Vec2(wx,wy))
                p = ObjectManager.c2py(p)
                if self._drag and self._drag._object is p:
                    continue
                if p and p in self._multi_objects:
                    under.append(p)
        if not pygame.mouse.get_focused():
            under = []
        self._update_under(under)
        for ev in evs:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self._clicking = under
                for object in under:
                    object.on_press()
                for e in self._click_objects:
                    l = e.get_root_layer()
                    if not l:
                        continue
                    wx,wy = self.get_relative_pos(l)
                    p = e._cObj.Pick(_c.Vec2(wx,wy))
                    p = ObjectManager.c2py(p)
                    if p and p in self._click_objects:
                        self._clicking.append(p)
                        p.on_press()
            elif ev.type == pygame.MOUSEBUTTONUP:
                if self._drag is not None:
                    self._drag._update_pos(mx,my)
                    self._drag._object.on_drag_end()
                    self._drag._object.on_release()                  
                    self._drag = None
                    self._clicking = []
                elif self._clicking != []:
                    for object in self._clicking:
                        if object in self._under:
                            object.on_click()
                    self._clicking = []
                for object in self._under:
                    object.on_release()
            elif ev.type == pygame.MOUSEMOTION and self._clicking != []:
                dragger = None
                if len(self._clicking) > 1:
                    results = []
                    i = 0
                    for object in self._clicking:
                        if not object.draggable:
                            continue
                        idx = scene.layers.index(
                                            object.get_root_layer().get_name())
                        results.append((idx, i, object))
                    results.sort()
                    dragger = results[-1][2]
                elif self._clicking[0].draggable:
                    dragger = self._clicking[0] 
                if self._drag is None and dragger is not None:
                    l = dragger.get_root_layer()
                    if l: 
                        wx,wy = self.get_relative_pos(l)
                        self._drag = Drag(dragger,(wx,wy))
                        dragger.on_drag_begin()
                        try:    
                            self._under.remove(dragger)
                        except:
                            pass
                    self._clicking = []
        if self._drag is not None:
            self._drag._update_pos(mx,my)
            self._drag._object.on_drag()

    def _update_under(self, under):
        if under != self._under:
            for object in under:
                if object not in self._under:
                    object.on_enter()
                else:
                    self._under.remove(object)
            for object in self._under:
                object.on_exit()
            self._under = under
            
    def is_under(self, obj):
        return obj in self._under
                    
    def pick_all(self, x, y):
        """pick_all(x,y)

Get all nodes whose rects overlap (x,y)
"""
        nodelist = PigDirector.scene.get_ordered_nodes()
        picklist = []
        for node in nodelist:
            l = node.get_root_layer()
            x,y = l.convert_pos(x,y)
            if node._cObj.Pick(_c.Vec2(x,y))        :
                picklist.append(node)
        return picklist

    def pick_selection(self, x, y, selectedObjectDict={}):
        """pick_selection(x, y, selectedObjectDict={})->node to select at x,y
        
x,y: coordinates
selectedObjectDict: a list of selected objects. If possible, pick will return an 
    object at x,y that is NOT in the list.
"""
        picklist = self.pick_all(x, y)
        if not len(picklist):
            return None
        if len(picklist) == 1 or not selectedObjectDict:
            return picklist[0]
        start_node = None
        selected_list = []
        for selected_node in selectedObjectDict:
            selected_list.append(selected_node)
            if not start_node and selected_node in picklist:
                start_node = selected_node
        if start_node:
            start_idx = picklist.index(start_node)
            idx = start_idx + 1
            while idx != start_idx:
                if idx >= len(picklist):
                    idx = 0
                try_node = picklist[idx]
                if try_node in selected_list:
                    idx = idx + 1
                    continue
                else:
                    return try_node
        else:
            return picklist[0]
    
class Drag(object):
    def __init__(self, object, xy):
        self.start_pos = xy
        self.prev_pos = xy
        self._object = object
        
    def _update_pos(self, x, y):
        wx,wy = PigDirector.scene.mouse_manager.get_relative_pos(
                                                self._object.get_root_layer())
        ox,oy = self.prev_pos
        dx = wx-ox
        dy = wy-oy
        self._object.position += (dx,dy)
        self.prev_pos = wx,wy