from Opioid2D.public.Node import Node

from pug.component import *

class Set_Gname(Component):
    "When owner is added to scene, it's gname is set to the given string"
    #component_info
    _set = 'pug_opioid'
    _type = 'settings'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['gname','gname to set owner to when added to scene'],                   
            ]
    #defaults
    gname = ''
    
    @component_method
    def on_added_to_scene(self, scene):
        """Start facing motion when object is added to scene"""
        if self.gname:
            self.owner.gname = self.gname

register_component( Set_Gname)
