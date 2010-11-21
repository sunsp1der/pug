import math

from Opioid2D.public.Node import Node
import Opioid2D

from pug.component import *
from pig.components import SpriteComponent

# TODO: need to make this far more robust, preferably with oollision sytem
class Motion_Zone(SpriteComponent):
    """Object cannot move beyond defined zone.
        
Warning: This component uses a tick_action, so it may be slow."""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['set_to_screen', "Set zone to screen size minus owner's image\n"+\
                        "size when added to scene. Other settings ignored."],
            ['x', "Left edge of zone"],
            ['y', "Top edge of zone"],
            ['width', "Width of zone"],
            ['height', "Height of zone"],
            ['xx', "Right edge of zone (ignore width)"],
            ['yy', "Bottom edge of zone (ignore height)"],
            ]
    #default    
    set_to_screen = True
    x = 0
    y = 0
    width = 0
    height = 0
    xx = None
    yy = None
    
    tick_action = None
    
    @component_method
    def on_added_to_scene(self):
        """Start timer when object is added to scene"""
        self.owner.do(Opioid2D.CallFunc( self.set_zone))
        
    def set_zone(self):
        owner = self.owner
        if self.set_to_screen:
            if owner.image:
                radius = math.hypot(owner.rect.height, owner.rect.width) * 0.5
            else:
                radius = 0
            self.x = 0 + radius
            self.y = 0 + radius
            view = Opioid2D.Display.get_view_size()
            self.xx = view[0] - radius
            self.yy = view[1] - radius
            self.width = self.height = self.radius = self.direction = self.arc\
                                                                         = None
            if self.xx is None:
                self.xx = self.x + self.width
            if self.yy is None:
                self.yy = self.y + self.height

        if not self.tick_action:
            self.tick_action = Opioid2D.TickFunc( self.check_motion_zone)
            self.tick_action.do()
        
    @component_method
    def on_destroy(self):
        "Abort the tick action on destroy"
        if self.tick_action:
            self.tick_action.abort() 
            
    def check_motion_zone(self):
        if not self.enabled:
            return
        position = self.owner.position
        if position.x < self.x:
            position.x = self.x    
        elif position.x > self.xx:
            position.x = self.xx    
        if position.y < self.y:
            position.y = self.y    
        elif position.y > self.yy:
            position.y = self.yy
        self.owner.set_position(position)    
                                                          
register_component( Motion_Zone)
                                                                         
