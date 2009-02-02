import random
import weakref
from inspect import isclass
from types import StringTypes

from Opioid2D import *
from Opioid2D.public.Node import Node

from pug.component import *
from pug import Dropdown

from pug_opioid.util import get_available_objects, get_project_object
from pug_opioid.editor.agui import ObjectsDropdown

class Spawn_Area(Component):
    """This object spawns other objects"""
    # component_info
    _set = 'pug_opioid'
    _type = 'spawn'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]    
    _field_list = [
        ["object", ObjectsDropdown, {'component':True,
                                     'doc':"The object class to spawn"}],
        ["spawn_interval",
                "Seconds between spawns (0 for no automatic spawning)"],
        ["spawn_variance",
                "spawn_interval can vary this many seconds"],
        ["spawn_delay","Wait this many seconds before beginning to spawn"],
        ["spawn_location", Dropdown, {'list':['area', 'center', 'edges', 'top',
                                              'bottom','left','right'], 
                            'doc':"The area where objects can be spawned"}],
        ["spawn_offset","Spawn location is offset by this much"],
        ["match_rotation","Rotate spawned object to this object's rotation"],
        ["match_velocity",
            "Set spawned object velocity to this object's velocity"],
        ["max_objects_spawned","Number of objects to spawn (-1 for unlimited)"],
        ["max_spawns_in_scene",
            "Maximum number of spawns in scene at one time (-1 for unlimited)"],
        ["delete_when_done",
   "Delete this object after the specified number of objects has been spawned"],
        ["owner_callback", 
            "\n".join(["Call this method of owner right after a spawn happens.",
                       "callback( spawned_object, this_component)"])],
        ["obj_callback", 
   "\n".join(["Call this method of spawned object right after a spawn happens.",
                       "callback( this_component)"])],
        ]
    # attribute defaults
    object = None
    spawn_interval = 2.0
    spawn_variance = 1.0
    spawn_delay = 0.0
    spawn_location = 'Area'
    spawn_offset = Vector(0,0)
    match_rotation = False
    match_velocity = False
    max_objects_spawned = -1
    max_spawns_in_scene = -1
    delete_when_done = True
    owner_callback = None
    obj_callback = None
    # other defaults
    last_object = None
    spawn_count = 0
    spawn_class = None
    spawned_objects = None
    action = None # the pending spawn action

    @component_method
    def on_added_to_scene(self):
        "on_added_to_scene(): Start spawn timer when object is added to scene"
        self.spawned_objects = weakref.WeakKeyDictionary()
        self.start_spawning()
        
    def start_spawning(self):
        "start_spawning: Start the spawn timer. To skip delay, call check_spawn"
        if self.spawn_interval > 0:
            self.action = self.owner.do( Delay(self.spawn_delay \
                   + random.uniform(-self.spawn_variance, self.spawn_variance))\
                   + CallFunc( self.check_spawn))
            
    @component_method
    def spawn(self):
        "spawn(): Spawn the chosen object"
        if self.object != self.last_object:
            self.spawn_class = get_project_object(self.object)            
        if not isclass(self.spawn_class) or not self.enabled:
            return None
        if not self.spawned_objects:
            self.spawned_objects = weakref.WeakKeyDictionary()
        obj = self.spawn_class( register=False)
        self.spawned_objects[obj] = self.spawn_count
        x_pos = 0
        y_pos = 0
        location = self.spawn_location
        #spawn_location can be Top, Bottom, Left, Right, Area, Center, Edges
        rect = self.owner.rect
        if location == "edges":
            location = random.choice(['top','bottom','left','right'])
        if location == "area":
            x_pos = random.uniform(0, rect.width)
            y_pos = random.uniform(0, rect.height)
        elif location == "center":
            x_pos = rect.centerx
            y_pos = rect.centery
        elif location == "top":
            x_pos = random.uniform(0, rect.width)
            y_pos = 0
        elif location == "bottom":
            x_pos = random.uniform(0, rect.width)
            y_pos = rect.height
        elif location == "right":
            x_pos = rect.width
            y_pos = random.uniform(0, rect.height)
        elif location == "left":
            x_pos = 0
            y_pos = random.uniform(0, rect.height)
        x_pos += self.spawn_offset[0] - rect.width*0.5
        y_pos += self.spawn_offset[0] - rect.height*0.5
        position = Vector(x_pos, y_pos)
        position.set_direction(position.get_direction() + self.owner.rotation)
        position += self.owner.position
        obj.position = position
        if self.match_rotation:
            obj.rotation = self.owner.rotation
        if self.match_velocity:
            obj.velocity = self.owner.velocity
        obj.do_register() # wait to activate object until start data set
        if self.owner_callback and hasattr(self.owner,'callback'):
            getattr(self.owner,'callback')(obj, self)
        if self.obj_callback and hasattr(obj,'callback'):
            getattr(obj,'callback')(self)
        self.spawn_count += 1
        if self.max_objects_spawned > -1 and \
                self.spawn_count >= self.max_objects_spawned and \
                self.delete_when_done:
            self.owner.do(Delete)
            print "spawn autodelete immediate deletion:",self.owner.deleted 
        return obj               
            
    def get_next_spawn_time(self):
        "get_next_spawn_time()-> how long to wait before next spawn"
        return self.spawn_interval + random.uniform(-self.spawn_variance, 
                                                self.spawn_variance)
        
    def check_spawn(self):
        """check_spawn(): do a spawn if criteria are met 
        
This method checks against max_spawns_in_scene and count. Another spawn will be
scheduled unless max_objects_spawned has been reached. """
        if self.max_objects_spawned > -1 and \
                self.spawn_count >= self.max_objects_spawned:
            return
        if not self.max_spawns_in_scene > -1 and \
                len(self.spawned_objects) > self.max_spawns_in_scene:
            self.spawn()
        if self.spawn_interval > 0:
            self.action = self.owner.do( Delay(self.get_next_spawn_time()) + \
                               CallFunc(self.check_spawn))
                    
    def stop_spawning(self):
        self.action.abort()
        
register_component( Spawn_Area)
