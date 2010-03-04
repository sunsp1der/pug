"Key_Spawn.py"
from pug import Dropdown
from pug.component import component_method, register_component

from Opioid2D.public.Node import Node

from pig.keyboard import keys
from pig.editor.agui import ObjectsDropdown, KeyDropdown
from pig.components.spawn.Spawn_Area import Spawn_Area
from pig.PigDirector import PigDirector

class Key_Spawn( Spawn_Area):
    """Owner spawns other objects when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ['key', KeyDropdown, {'doc':"Press this key to spawn"}],                   
        ["object", ObjectsDropdown, {'component':True,
                                     'doc':"The object class to spawn"}],
        ["spawn_location", Dropdown, {'list':['area', 'center', 'edges', 'top',
                                              'bottom','left','right'], 
                            'doc':"The area where objects can be spawned"}],
        ["spawn_offset", 
         "Spawn location is offset by this much (scaled by owner size)"],
        ["min_objects_per_spawn","Minimum number of objects created"],
        ["max_objects_per_spawn","Maximum number of objects created"],
        ["max_spawns_in_scene",
            "Maximum number of spawns in scene at one time (-1 = unlimited)"],        
        ["match_scale", "Multiply spawned object's scale by owner's scale"],
        ["add_rotation", "Add owner's rotation to spawned object's rotation"],
        ["add_velocity", "Add owner's velocity to spawned object's velocity"],
        ["owner_callback", 
            "\n".join(["Call this method of owner right after a spawn happens.",
                       "callback( spawned_object, this_component)"])],        
        ["obj_callback", 
   "\n".join(["Call this method of spawned object right after a spawn happens.",
                       "callback( this_component)"])],
        ]
    
    key = keys["SPACE"]

    @component_method
    def on_added_to_scene(self, scene):
        "Set spawn key"
        self.k_info = [None,]
        self.k_info[0] = scene.register_key_down( self.key, self.spawn)

    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        for info in self.k_info:
            scene.unregister_key(info)
 
register_component( Key_Spawn)
        
       
