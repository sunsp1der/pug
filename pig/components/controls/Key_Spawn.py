"Key_Spawn.py"
from pug.component import component_method, register_component

from Opioid2D.public.Node import Node

from pig.actions import Delay, CallFunc
from pig.editor.agui import KeyDropdown
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
        ['rapid_fire', 'Holding down key spawns continuously'],
        ]
    _field_list += Spawner._field_list
    
    key = "SPACE"
    spawn_interval = 0.5
    spawn_interval_variance = 0.0
    rapid_fire = True
    
    interval_complete = True  
    
    @component_method
    def on_added_to_scene(self):
        "Set spawn key and setup the spawner"
        scene = PigDirector.scene
        self.setup_spawner()
        self.interval_complete = False
        self.k_info = [0,0]
        self.k_info[0] = scene.register_key_down( self.key, self.check_spawn)
        self.k_info[1] = scene.register_key_up( self.key, self.stop_spawning)
        self.interval_complete = True
    
    def check_spawn(self, schedule_next=False):
        if not self.enabled:
            return
        self.spawning = True
        if self.interval_complete:  
            # spawn_interval has completed          
            spawns = Spawner.check_spawn(self, schedule_next)
            if spawns:
                # we just spawned so we need to wait for interval again
                self.interval_complete = False
                # get next spawn_interval
                interval = self.get_next_spawn_wait()
                # set a timer to change interval_complete to True
                self.owner.do( Delay(interval) + CallFunc(self.set_complete, 
                                                          True))

    def set_complete(self, val):
        self.interval_complete = val
        if self.rapid_fire and self.owner and self.spawning:
            # when rapid_firing, we CAN shoot, so try to shoot!
            self.check_spawn()
            
    def stop_spawning(self):
        self.spawning = False
        
    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        for k in self.k_info:
            scene.unregister_key(k)
        self.k_info = []
 
register_component( Key_Spawn)
        
       
