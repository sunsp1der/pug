import math

from Opioid2D.public.Node import Node
import Opioid2D

from pug.component import *

from pig.PigDirector import PigDirector
from pig.components import SpriteComponent

class Life_Zone(SpriteComponent):
    """Object is deleted if it leaves the given zone."""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['set_to_screen', "Set zone to screen size plus owner's image\n"+\
                        "size when added to scene. Other settings ignored."],
            ['x', "Left edge of zone"],
            ['y', "Top edge of zone"],
            ['width', "Width of zone"],
            ['height', "Height of zone"],
            ['xx', "Right edge of zone (ignore width)"],
            ['yy', "Bottom edge of zone (ignore height)"],
            ['radius', 
             "Zone is circle of this radius from origin (ignore width/height)"],
            ['direction', "Start direction of semi-circular zone arc"],
            ['arc', "Arc of semi-circular zone"],
            ['group_name', "Each different zone creates a scene group.\n"+
                            "None: automatically generated name,"]
            ]
    #defaults
    set_to_screen = True
    x = 0
    y = 0
    width = 0
    height = 0
    xx = None
    yy = None
    radius = None
    direction = None
    arc = None
    group_name = None
    
    #other defaults
    zone_groups = {} # dict of args:group so we don't duplicate 'em
    zonetype = Opioid2D.mutators.LifeZone
    
    @component_method
    def on_added_to_scene(self):
        """Start timer when object is added to scene"""
        self.owner.do(Opioid2D.CallFunc( self.set_zone))
        
    @component_method
    def on_exit_scene(self, scene):
        if self.zone_groups:
            Life_Zone.zone_groups = {}
        
    def set_zone(self):
        owner = self.owner
        if self.set_to_screen:
            if owner.image:
                radius = math.hypot(owner.rect.height, owner.rect.width) * 0.5
            else:
                radius = 0
            self.x = 0 - radius
            self.y = 0 - radius
            view = Opioid2D.Display.get_view_size()
            self.xx = view[0] + radius
            self.yy = view[1] + radius
            self.width = self.height = self.radius = self.direction = self.arc\
                                                                         = None
        args = (self.x, self.y, self.width, self.height, 
                       self.xx, self.yy, self.radius, self.direction, self.arc)
        group = self.zone_groups.get(args)
        if not group or group not in PigDirector.scene._groups:
            if self.group_name:
                group = str(self.group_name)
            else:
                group = ''.join(["lifezone_", str(len(self.zone_groups))])
            scene = Opioid2D.Director.scene
            scene.get_group(group).add_mutator(self.zonetype( *args))
            self.zone_groups[args] = group
        owner.join_group(group)
            
register_component( Life_Zone)
