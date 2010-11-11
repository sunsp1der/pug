from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import Component, register_component, component_method
from pug.gname import get_gnamed_object_list

from pig.components.spawn.Spawned_Attribute import Spawned_Attribute
from pig.components.controls.Key_Component import Key_Component
from pig.components.behavior.Set_Attribute import Set_Attribute

class Spawned_Component( Spawned_Attribute):
    """When this object spawns another object, change an attribute on the
spawned object. If multiple component's have the same name, they will all be 
altered."""
    #component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['spawner_name', MyComponents, 
                    {'doc':'Name of the spawner component. '+\
                            'If blank, all spawners will be affected.'}],
            ['component_name',
                    "Name of the spawned object's component(s) to alter"]
            ]
    _field_list += Set_Attribute._field_list
    # defaults
    component_name = ""
    
    stripped_name = ""
    
    @component_method                
    def on_spawn( self, object, component):
        if not self.component_name:
            return
        if not self.stripped_name or self.stripped_name == component.gname:
            if object is None:
                list = get_gnamed_object_list(self.component_name)
                for object in list:
                    try:
                        owner = object.owner
                    except:
                        continue
                    if self.owner == owner:
                        Set_Attribute.do_change(self, object)
            else:
                Set_Attribute.do_change(self, object)
                

register_component( Spawned_Component)