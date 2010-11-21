from Opioid2D import RealTickFunc, RotateTo, CallFunc
from Opioid2D.public.Node import Node
from Opioid2D.public.Math import angledelta

from pug import get_gnamed_object, GnameDropdown
from pug.component import *

from pig.components import SpriteComponent
from pig.util import angle_to

class Face_Object( SpriteComponent):
    """Object turns to face another object"""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['target', GnameDropdown,{'doc':'Object to face towards', 
                                      'class_list':[Node]}],
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
    tick_action = None
    
    @component_method
    def on_first_display(self):
        """Start facing target when object is added to scene"""
        self.end_action = CallFunc(self.target_reached)
        self.start_facing_target()
        
    @component_method
    def start_facing_target(self, target=None):
        "start_facing_target(target=None): if target is None, use target field"
        self.stop_facing_target()
        if target:
            self.target = target
        self.tick_action = RealTickFunc( self.check_facing).do()
        self.check_facing() # prevents jerky start
        
    @component_method
    def stop_facing_target(self):
        "Stop facing current target"
        if self.tick_action:
            self.tick_action.abort()
            
    @component_method
    def on_delete(self):
        "Abort the tick action on delete"
        if self.tick_action:
            self.tick_action.abort()            
        
    def check_facing(self, position=None):
        """check_facing(position=None)
        
position: an Opioid vector        
Turn the object toward position. If None, use obj.position"""
        if not self.enabled: 
            self.action.abort()
            return
        if position is None:
            if not self.target:
                return
            obj = get_gnamed_object(self.target)
            if not obj:
                return
            position = obj.position
        target_angle = angle_to(self.owner.position, 
                         position) + self.offset
        if self.rotation_speed < 0:
            # set owner to proper rotation instantly
            self.owner.rotation = target_angle
        else:
            if self.target_angle != target_angle:
            #create an action that will rotate owner to proper angle
                if self.action:
                    self.action.abort()
                self.action = (RotateTo(target_angle, 
                                        speed=self.rotation_speed) + \
                                self.end_action).do(self.owner)                        
                self.target_angle = target_angle
            if self.owner.rotation == self.target_angle:
                self.target_reached()
                    
    def target_reached(self):
        # opioid has a problem aborting the action if it's complete
        if self.action:
            self.action = None
        
register_component( Face_Object)
