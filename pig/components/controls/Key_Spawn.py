"Key_Spawn.py"
from pug import Dropdown
from pug.component import component_method, register_component

from Opioid2D.public.Node import Node

from pig.keyboard import keys
from pig.audio import get_sound
from pig.editor.agui import ObjectsDropdown, KeyDropdown, SoundFile
from pig.components.spawn.Spawner import Spawner
from pig.PigDirector import PigDirector

class Key_Spawn( Spawner):
    """Owner spawns other objects when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ['key', KeyDropdown, {'doc':"Press this key to spawn"}],                   
        ["spawn_object", ObjectsDropdown, {'component':True,
                                     'doc':"The object class to spawn"}],
        ["sound", SoundFile, {'doc':"Sound to play when a spawn occurs"}],                                     
        ["spawn_location", Dropdown, {'list':['area', 'center', 'edges', 'top',
                                              'bottom','left','right'], 
                            'doc':"The area where objects can be spawned"}],
        ["spawn_offset", 
         "Spawn location is offset by this much (0 to 1, 0 to 1). (0,0) "+\
         "is top-left, (0.5,0.5) is center, (1,1) is bottom-right etc."],
        ["obs_per_spawn","Number of objects created per spawn"],
        ["obs_per_spawn_variance",
                    "obs_per_spawn can vary by this much"],
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
        "Set spawn key and setup the spawner"
        self.k_info = scene.register_key_down( self.key, self.spawn)
        self.setup_spawner()        

    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        scene.unregister_key(self.k_info)
        self.k_info = []
 
register_component( Key_Spawn)
        
       
