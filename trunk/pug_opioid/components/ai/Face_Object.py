from Opioid2D import RealTickFunc, RotateTo, CallFunc
from Opioid2D.public.Node import Node

from pug import get_gnamed_object
from pug.component import *

from pug_opioid.util import angle_to
from pug_opioid.editor.util import GNAMED_NODE

class Face_Object(Component):
    """Object turns towards another given object"""
    #component_info
    _set = 'pug_opioid'
    _type = 'ai'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _attribute_list = [
            ['target', 'Object to face towards', GNAMED_NODE],
            ['rotation_speed',
                    'Speed to turn. Negative = always face object exactly.'],
            ['offset', 'Offset the rotation by this much']
            ]
    #defaults
    target = ''
    rotation_speed = -1
    offset = 0
    target_angle = None
    action = None
    
    @component_method
    def on_added_to_scene(self):
        """Set the rotation when object is added to scene"""
        act = RealTickFunc( self.check_facing)
        act.do()
        
    def check_facing(self):
        if not self.enabled:
            return
        obj = get_gnamed_object(self.target)
        if obj:
            target_angle = angle_to(self.owner.position, 
                             obj.position) + self.offset
            if self.rotation_speed < 0:
                # set owner to proper rotation instantly
                self.owner.rotation = target_angle
            else:
                #create an action that will rotate owner to proper angle
                if self.owner.rotation != target_angle:
                    if self.target_angle != target_angle:
                        if self.action:
                            self.action.abort()
                        action = RotateTo(target_angle, 
                                    speed=self.rotation_speed) + \
                                          CallFunc(self.target_reached)
                        self.action = action.do(self.owner)
                        self.target_angle = target_angle
    
    def target_reached(self):
        # opioid has a problem aborting the action if it's complete
        self.action = None
        
register_component( Face_Object)