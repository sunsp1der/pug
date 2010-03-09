"""Collision_Callback.py

This is the base component for all collision components. Because it calls
owner's on_collision callback, it allows components derived from it to react to
that callback. It also takes care of tracking sprite group names, so that PUG
can give the user a nice dropdown of all group names used in the scene.
"""

from weakref import ref

from Opioid2D.public.Sprite import Sprite

from pug.component import *

from pig.PigDirector import PigDirector
from pig.editor.agui.group_dropdown import GroupDropdown, register_group


class Collision_Callback( Component):
    """Object's "on_collision" method is called when it collides
    
arguments: on_collision( toSprite, fromSprite, toGroup, my_group)
"""
    #component_info
    _set = 'pig'
    _type = 'collision'
    _class_list = [Sprite]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['with_group', GroupDropdown, {'doc':"Group to collide with"}],
            ['my_group', GroupDropdown, 
                    {'doc':
                    "The group this object joins and uses for collision tests"}]
            ]
    # defaults
    _with_group = "all_colliders"
    _my_group = "all_colliders"
    
    @component_method
    def on_added_to_scene(self, scene):
        "Register for object.on_collision callback when object added to scene"
        self.owner.join_group( self._my_group)
        PigDirector.scene.register_collision_callback( self.owner, 
                                                    self.owner.on_collision,
                                                    self.with_group,
                                                    self.my_group,
                                                    ignore_duplicate=True)
        
    @component_method
    def on_collision(self, toSprite, fromSprite, toGroup, my_group):
        "This component doesn't do anything in the on_collision callback"
        pass
        
### track all available groups for editor dropdowns
    def __init__(self, *args, **kwargs):
        self.ref = ref(self)
        Component.__init__(self,  *args, **kwargs)

    def __del__(self):
        "__del__(): when component is deleted, unregister groups from gui"
        if self.ref():
            register_group( (self.ref, "with_group"), None)        
            register_group( (self.ref, "my_group"), None)        
        
    def get_with_group(self):
        return self._with_group
    def set_with_group(self, group):
        register_group( (self.ref, "with_group"), group)        
        self._with_group = group
    with_group = property (get_with_group, set_with_group)

    def get_my_group(self):
        return self._my_group
    def set_my_group(self, group):
        register_group( (self.ref, "my_group"), group)        
        self._my_group = group
    my_group = property (get_my_group, set_my_group)
    
register_component( Collision_Callback)
