from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import Component, register_component, component_method

from pig.components import SpriteComponent

class Spawn_Flower( SpriteComponent):
    """When this object spawns another object, the spawn is repeated at 
different angles. Use this with other spawn components or objects with an 
on_spawn callback"""
    #component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['petals', 'Number of spawn directions including original.'],
            ['spawner_name', MyComponents, 
                    {'doc':'Name of the spawner component. '+\
                            'If blank, all spawners will be affected.'}],                    
            ]
    # defaults
    petals = 5
    rotation_range = 360
    spawner_name = ""
    
    flowering = None
        
    @component_method                
    def on_spawn( self, obj, component):
        "Trigger extra spawns at new angles."
        if self.spawner_name and self.spawner_name != component.gname:
            return 
        if self.flowering is None:
            # the spawning is just starting
            self.flowering = component # the spawning component
        else:
            # this is a spawn created by this component. Don't flower it.
            return
        self.start_rotation = self.owner.rotation
        # how much to rotate for each copy
        rotation = 360 / float(self.petals)
        # flower the spawn
        for i in range(self.petals - 1):
            # next rotation
            self.owner.rotation += rotation
            # this component works through recursion... the spawn call below
            # will end up calling this on_spawn function again 
            component.spawn()
        # return to non-flowering state   
        self.flowering = None
        self.owner.rotation = self.start_rotation

register_component( Spawn_Flower)