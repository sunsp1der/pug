from weakref import ref

from Opioid2D.public.Sprite import Sprite

from pug.component import *

from pig.editor.agui.group_dropdown import *

class Join_Group( Component):
    """Object joins a sprite group for collisions or other uses."""
    #component_info
    _set = 'pig'
    _type = 'collision'
    _class_list = [Sprite]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['group', GroupDropdown, {'doc':"Group to join"}]
            ]
    # defaults
    _group = "colliders"

    @component_method
    def on_added_to_scene(self, scene):
        self.owner.join_group( self.group)
        
### track all available groups for editor dropdowns
    def __init__(self, *args, **kwargs):
        self.ref = ref(self)
        Component.__init__(self,  *args, **kwargs)

    def __del__(self):
        try:
            register_group( (self.ref, "group"), None)
        except:
            pass

    def get_group(self):
        return self._group
    def set_group(self, group):
        register_group( (self.ref, "group"), group)
        self._group = group
    group = property (get_group, set_group)
        
register_component( Join_Group)