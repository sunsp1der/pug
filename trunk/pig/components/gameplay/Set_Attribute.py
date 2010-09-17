from Opioid2D.public.Node import Node
from Opioid2D.public.Scene import Scene

from pug.component import *

class Set_Attribute(Component):
    "When owner is added to scene, an attribute is set to a given value."
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node, Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['attribute',"Owner's attribute to set"],
            ['value',"Value to set it to. Use quotes for strings."]                   
            ]
    #defaults
    attribute = ''
    value = ''
    
    @component_method
    def on_added_to_scene(self, scene):
        """Set gname when object is added to scene"""
        if self.attribute:
            setattr(self.owner, self.attribute, self.value)

register_component( Set_Attribute)
