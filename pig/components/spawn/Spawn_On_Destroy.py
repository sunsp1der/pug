"Spawn_On_Destroy.py"
from pug import Dropdown
from pug.component import component_method, register_component

from Opioid2D.public.Node import Node

from pig.editor.agui import ObjectsDropdown, SoundFile
from pig.components import Spawner

class Spawn_On_Destroy( Spawner):
    """Owner spawns other objects when destroyed"""
    # component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes:   
    _field_list = [
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
        ["match_scale", "Multiply spawned object's scale by owner's scale"],
        ["add_rotation", "Add owner's rotation to spawned object's rotation"],
        ["add_velocity", "Add owner's velocity to spawned object's velocity"],
        ["obj_callback", 
   "\n".join(["Call this method of spawned object right after a spawn happens.",
                       "callback( this_component)"])],
        ]

    @component_method
    def on_added_to_scene(self, scene):
        "Setup the spawner"
        self.setup_spawner()

    @component_method
    def on_destroy(self):
        "Do spawn when object is destroyed"
        self.spawn()      
 
register_component( Spawn_On_Destroy)
        
       
