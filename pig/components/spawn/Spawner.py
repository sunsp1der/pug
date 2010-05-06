import random
import weakref
from inspect import isclass

from Opioid2D import *
from Opioid2D.public.Node import Node

from pug.component import *
from pug import Dropdown

from pig.util import get_project_object
from pig.audio import get_sound
from pig.editor.agui import ObjectsDropdown, SoundFile

class Spawner(Component):
    """Owner spawns other objects"""
    # component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["spawn_object", ObjectsDropdown, {'component':True,
                                     'doc':"The object class to spawn"}],
        ["sound", SoundFile, {'doc':"Sound to play when a spawn occurs"}],
        ["spawn_interval",
                "Seconds between spawns (0 for no automatic spawning)"],
        ["spawn_variance",
                "spawn_interval can vary this many seconds"],
        ["spawn_location", Dropdown, {'list':['area', 'center', 'edges', 'top',
                                              'bottom','left','right'], 
                    'doc':"The area where objects can be spawned. All\n"+\
                          "locations except 'center' are randomized areas."}],
        ["spawn_offset", 
         "Spawn location is offset by this much (scaled by owner size)"],
        ["spawn_delay","Wait this many seconds before beginning to spawn"],
        ["min_objects_per_spawn","Minimum number of objects created per spawn"],
        ["max_objects_per_spawn","Maximum number of objects created per spawn"],
        ["max_objects_spawned",
"Total number of objects owner can create over its lifetime (-1 = unlimited)"],
        ["max_spawns_in_scene",
            "Maximum number of spawns in scene at one time (-1 = unlimited)"],
        ["match_scale", "Multiply spawned object's scale by owner's scale"],
        ["add_rotation", "Add owner's rotation to spawned object's rotation"],
        ["add_velocity", "Add owner's velocity to spawned object's velocity"],
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
    spawn_object = None
    sound = None
    spawn_interval = 2.0
    spawn_variance = 1.0
    spawn_delay = 0.0
    spawn_location = 'center'
    spawn_offset = (0,0)
    min_objects_per_spawn = 1
    max_objects_per_spawn = 1
    match_scale = True
    add_rotation = True
    add_velocity = False
    max_objects_spawned = -1
    max_spawns_in_scene = -1
    delete_when_done = True
    owner_callback = None
    obj_callback = None
    # other defaults
    last_object = None
    sound_object = None
    spawn_count = 0
    spawn_class = None
    spawned_objects = None
    action = None # the pending spawn action

    @component_method
    def on_added_to_scene(self, scene):
        "Start spawn timer when object is added to scene"
        if self.sound:
            self.sound_object = get_sound( self.sound)
        self.start_spawning()
        
    def start_spawning(self):
        "Start the spawn timer. To skip delay, call check_spawn"
        if self.spawn_interval > 0:
            self.action = self.owner.do( Delay(self.spawn_delay \
                   + random.uniform(-self.spawn_variance, self.spawn_variance))\
                   + CallFunc( self.check_spawn))
    
    @component_method 
    def spawn(self):
        "spawn()->[objects_spawned]: spawn objects"
        if self.spawn_object != self.last_object:
            self.spawn_class = get_project_object(self.spawn_object)
        if not isclass(self.spawn_class) or not self.enabled:
            return []
        if self.spawned_objects is None:
            self.spawned_objects = weakref.WeakValueDictionary()
        owner = self.owner
        spawned_objects = []
        count = random.randint(self.min_objects_per_spawn,
                               self.max_objects_per_spawn)
        rect = owner.rect
        rotation = owner.rotation
        position = owner.position
        velocity = owner.velocity
        scale = owner.scale
        for i in range(count):
            if self.max_objects_spawned > -1 and \
                    self.spawn_count >= self.max_objects_spawned:
                if self.delete_when_done:
                    owner.do(Delete())
                break
            if self.max_spawns_in_scene > 0 and \
                    len(self.spawned_objects) >= self.max_spawns_in_scene:
                break            
            obj = self.spawn_class( register=False)
            self.spawned_objects[self.spawn_count] = obj
            x_pos = 0
            y_pos = 0
            location = self.spawn_location
            #spawn_location can be Top, Bottom, Left, Right, Area, Center, Edges
            halfwidth = rect.width * 0.5
            halfheight = rect.height * 0.5
            if location == "edges":
                location = random.choice(['top','bottom','left','right'])
            if location == "area":
                x_pos = random.uniform(0, rect.width)
                y_pos = random.uniform(0, rect.height)
            elif location == "center":
                x_pos = halfwidth
                y_pos = halfheight
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
            x_pos += self.spawn_offset[0] * halfwidth - halfwidth
            y_pos += self.spawn_offset[1] * halfheight - halfheight
            obj.position = Vector(x_pos, y_pos)
            obj.position.direction += rotation
            obj.position += position
            if self.match_scale:
                obj.scale = obj.scale * scale
            if self.add_rotation:
                obj.rotation += rotation
                obj.velocity.direction += rotation
                obj.acceleration.direction += rotation
            if self.add_velocity:
                obj.velocity += velocity
            obj.do_register() # wait to activate object until start data set
            if self.owner_callback and hasattr(owner, self.owner_callback):
                getattr(owner,'callback')(obj, self)
            if self.obj_callback and hasattr(obj, self.obj_callback):
                getattr(obj,'callback')(self)
            self.spawn_count += 1
            spawned_objects.append(obj)
        if spawned_objects and self.sound_object:
            self.sound_object.play()            
        return spawned_objects               
            
    def get_next_spawn_time(self):
        "get_next_spawn_time()-> how long to wait before next spawn"
        return self.spawn_interval + random.uniform(-self.spawn_variance, 
                                                self.spawn_variance)
        
    def check_spawn(self, schedule_next=True):
        """check_spawn(): do a spawn if criteria are met 
        
This method checks against max_spawns_in_scene and count. Another spawn will be
scheduled unless max_objects_spawned has been reached. """
        if self.max_objects_spawned > -1 and \
                self.spawn_count >= self.max_objects_spawned:
            return None
        if self.spawn_interval > 0 and schedule_next:
            self.action = self.owner.do( Delay(self.get_next_spawn_time()) + \
                                         CallFunc(self.check_spawn))
        if self.max_spawns_in_scene < 0 or \
                len(self.spawned_objects) < self.max_spawns_in_scene:
            return self.spawn()
        return None
                    
    def stop_spawning(self):
        self.action.abort()
    
    def pop_spawned(self):
        """pop_spawned(): pop and return a spawned object"""
        return self.spawned_objects.popitem()[1]
    
        
register_component( Spawner)
