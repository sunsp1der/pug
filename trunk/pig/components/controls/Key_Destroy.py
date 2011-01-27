"Key_Destroy.py"
from pug.component import *

from Opioid2D.public.Node import Node

from pig.editor.agui import KeyDropdown
from pig.keyboard import keys

from pig.PigDirector import PigDirector
from pig.components import SpriteComponent

class Key_Destroy( SpriteComponent):
    """Owner destroys itself when a key is pressed or released"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ['key', KeyDropdown, 
                {'doc':"The key that triggers owner destroying itself"}],                   
        ['press',"Destroy owner when key is pressed"],                   
        ['release',"Destroy owner when key is released"],                   
        ]
    
    key = "SPACE"
    press = True
    release = True
    k_info = []
    
    @component_method
    def on_added_to_scene(self):
        "Set spawn key and setup the spawner"
        scene = PigDirector.scene
        if self.press:
            self.k_info.append( scene.register_key_down( self.key, 
                                                         self.owner.destroy))
        if self.release:
            self.k_info.append( scene.register_key_up( self.key, 
                                                       self.owner.destroy))

    @component_method
    def on_destroy(self):
        """unregister keys"""
        scene = PigDirector.scene
        for k in self.k_info:
            scene.unregister_key(k)
        self.k_info = []
        
    @component_method
    def on_delete(self):
        """unregister keys"""
        self.on_destroy()
 
register_component( Key_Destroy)
        
       
