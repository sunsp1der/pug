from Opioid2D.public.Sprite import Sprite
from Opioid2D import Director

from pug.component import *

class Join_Group( Component):
    """Object joins a sprite group for collisions or other uses."""
    #component_info
    _set = 'pig'
    _type = 'collision'
    _class_list = [Sprite]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['group', "Group to join"]
            ]
    # defaults
    _group = "all_colliders"
    
    @component_method
    def on_added_to_scene(self, scene):
        self.owner.join_group( self.group)
        
    # track all available groups for editor dropdowns
    def get_group(self):
        return self._group
    def set_group(self, group):
        self._group = group
    group = property (get_group, set_group)
    
register_component( Join_Group)