"""Collision_Callback.py

This is the base component for all collision components. Because it calls
owner's on_collision callback, it allows components derived from it to react to
that callback. It also takes care of tracking sprite group names, so that PUG
can give the user a nice dropdown of all group names used in the scene.
"""

from Opioid2D.public.Sprite import Sprite
from pig.PigDirector import PigDirector

from pug.component import *

class Collision_Callback( Component):
    """Object's "on_collision" method is called when it collides
    
arguments: on_collision( toSprite, fromSprite, toGroup, fromGroup)
"""
    #component_info
    _set = 'pig'
    _type = 'collision'
    _class_list = [Sprite]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['withGroup', "Group to collide with"],
            ['fromGroup', "Group to join and use for collision tests"]
            ]
    # defaults
    _withGroup = "all_colliders"
    _fromGroup = "all_colliders"
    
    @component_method
    def on_added_to_scene(self, scene):
        self.owner.join_group( self._fromGroup)
        PigDirector.scene.register_collision_callback( self.owner, 
                                                    self.owner.on_collision,
                                                    self.withGroup,
                                                    self.fromGroup)
        
    # track all available groups for editor dropdowns
    def get_withGroup(self):
        return self._withGroup
    def set_withGroup(self, group):
        self._withGroup = group
    withGroup = property (get_withGroup, set_withGroup)

    def get_fromGroup(self):
        return self._fromGroup
    def set_fromGroup(self, group):
        self._fromGroup = group
    fromGroup = property (get_fromGroup, set_fromGroup)
    
register_component( Collision_Callback)
