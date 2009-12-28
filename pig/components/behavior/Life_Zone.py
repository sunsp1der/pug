import math
from Opioid2D.public.Node import Node
import Opioid2D

from pug.component import *

class Life_Zone(Component):
    """Object is deleted if it leaves the given zone."""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['set_to_screen', 
"""Set zone to screen size plus owner's image size 
when added to scene. Other settings ignored."""],
            ['x', "Left origin of zone"],
            ['y', "Top origin of zone"],
            ['width', "Width of zone"],
            ['height', "Height of zone"],
            ['xx', "Right corner of zone (ignore width)"],
            ['yy', "Bottom corner of zone (ignore height)"],
            ['radius', 
             "Zone is circle of this radius from origin (ignore width/height)"],
            ['direction', "Start direction of semi-circular zone arc"],
            ['arc', "Arc of semi-circular zone"],
            ['group_name', 
"""Each different zone creates a scene group. 
None: automatically generated name,"""]
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
    def on_added_to_scene(self, scene):
        """Start timer when object is added to scene"""
        self.set_zone()
        
    @component_method
    def on_exit_scene(self, scene):
        if self.zone_groups:
            Life_Zone.zone_groups = {}
        
    def set_zone(self):
        owner = self.owner
        if self.set_to_screen:
            if owner.image:
                radius = math.hypot(owner.image.height, 
                                    owner.image.width) * 0.5
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
        if not group:
            if self.group_name:
                group = str(self.group_name)
            else:
                group = ''.join(["lifezone_", str(len(self.zone_groups))])
            scene = Opioid2D.Director.scene
            scene.get_group(group).add_mutator(self.zonetype( *args))
            self.zone_groups[args] = group
        owner.join_group(group)
            
register_component( Life_Zone)
