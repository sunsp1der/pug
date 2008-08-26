from Opioid2D.public.Node import Node
from pug.component import *

class Set_Rotation_Speed(Component):
    """Set object's rotation speed when it's added to a scene."""
    _set = 'pug_opioid'
    _type = 'physics'
    _class_list = [Node]
    _attribute_dict = {
           'rotation_speed':'Speed to set rotation to'
    }
    
    rotation_speed = 30
    
    @component_method
    def on_added_to_scene(self, owner, scene):
        owner.rotation_speed += self.rotation_speed
        
register_component( Set_Rotation_Speed)