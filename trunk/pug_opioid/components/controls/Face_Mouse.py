from Opioid2D import Mouse
from Opioid2D.public.Node import Node

from pug_opioid.components import Face_Object

class Face_Mouse( Face_Object):
    """Object turns to face the mouse"""
    #component_info
    _set = 'pug_opioid'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['rotation_speed',
                    'Speed to turn. Negative = always face object exactly.'],
            ['offset', 'Offset the rotation by this much']
            ]
                
    def check_facing(self, position=None):
        """check_facing(position=None)
        
position: an Opioid vector        
Turn the object toward position. If None, use mouse position."""
        if position is None:
            position = Mouse.position
        Face_Object.check_facing(self, position)
                
from pug.component import register_component
register_component( Face_Mouse)
