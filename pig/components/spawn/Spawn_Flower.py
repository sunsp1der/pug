from Opioid2D.public.Node import Node

from pug.component import Component, register_component, component_method

class Spawn_Flower( Component):
    """When this object spawns another object, the spawn is repeated at 
different angles. Use this with other spawn components or objects with an 
on_spawn callback"""
    #component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['copies', 'Number of copies to create.'],
            ['rotation', 
                    'Each copy created as if owner had rotated this much'],
            ['h_symmetry',
        'Objects created at 180-360 rotation will be flipped horizontally'],
            ['v_symmetry',
        'Objects created at 90-270 rotation will be flipped vertically'],
            ]
    # defaults
    copies = 4
    rotation = 72
    h_symmetry = False
    v_symmetry = False
    
    flowering = None
        
    @component_method                
    def on_spawn( self, obj, component):
        if self.flowering is None:
            self.flowering = component
        else:
            rot = self.rot % 360
            if self.h_symmetry:
                if 180 < rot < 360 or rot == 0:
                    obj.scale.x *= -1
            if self.v_symmetry:
                if 90 < rot < 270:
                    obj.scale.x *= -1
            return
        self.start_rotation = self.owner.rotation
        self.rot = 0
        for i in range(self.copies):
            self.owner.rotation += self.rotation
            self.rot += self.rotation
            objects = component.spawn()
            
        self.flowering = None
        self.owner.rotation = self.start_rotation

register_component( Spawn_Flower)