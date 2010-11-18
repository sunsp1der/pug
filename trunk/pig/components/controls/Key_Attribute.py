"Key_Attribute.py"
from copy import deepcopy

from Opioid2D.public.Vector import VectorReference
from Opioid2D.public.Node import Node

from pug import Dropdown, Generic
from pug.component import *

from pig.components.behavior.Set_Attribute import Set_Attribute
from pig.editor.agui import KeyDropdown
from pig.keyboard import keys
from pig.PigDirector import PigDirector

class Key_Attribute( Set_Attribute):
    """Change owner's attribute when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ['key', KeyDropdown, 
                {'doc':"The key that triggers owner destroying itself"}],
        ['key_up_undo',
                    "Return attribute to original value when key is released"]                     
        ]
    _field_list += Set_Attribute._field_list
    
    key = "SPACE"
    key_up_undo = True
    
    @component_method
    def on_added_to_scene(self):
        "Set spawn key and setup the spawner"
        scene = PigDirector.scene
        self.k_info = [0,0]
        self.k_info[0] = scene.register_key_down( self.key, 
                                                  self.do_change)
        self.k_info[1] = scene.register_key_up( self.key, 
                                                self.undo_change)
            
    def undo_change(self, object=None):
        """undo_change(object=None): undo change defined by component
        
object: the object to be changed. This allows easy over-riding of this function
in derived components.
"""
        if not self.key_up_undo:
            return
        Set_Attribute.undo_change(self)

    @component_method
    def on_destroy(self):
        """unregister keys when component is destroyed"""
        scene = PigDirector.scene
        for k in self.k_info:
            scene.unregister_key(k)
        self.k_info = []
 
register_component( Key_Attribute)
        
       
