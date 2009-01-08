from Opioid2D.public.Node import Node
from pug.component import *

class Set_Rotation_Speed(Component):
    """Set object's rotation speed when it's added to a scene"""
    _set = 'pug_opioid'
    _type = 'physics'
    _class_list = [Node]
    _attribute_list = [
           ['rotation_speed', 'Speed to set rotation to'],
           ['additive', 
"""Add to current rotation instead of setting it"""]
    ]
    
    rotation_speed = 30
    additive = False
    
    @component_method
    def on_added_to_scene(self):
        """Set the rotation when object is added to scene"""
        if self.additive:
            self.owner.rotation_speed += self.rotation_speed
        else:
            self.owner.rotation_speed = self.rotation_speed
        
register_component( Set_Rotation_Speed)