from Opioid2D.public.Node import Node

from pug.component import *

class Set_Gname(Component):
    "When owner is added to scene, it's gname is set to the given string"
    #component_info
    _set = 'pig'
    _type = 'gameplay'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['gname','gname to set owner to when added to scene'],                   
            ]
    #defaults
    gname = ''
    
    @component_method
    def on_added_to_scene(self, scene):
        """Set gname when object is added to scene"""
        if self.gname:
            self.owner.gname = self.gname

register_component( Set_Gname)
