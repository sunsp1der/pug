from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import Component, register_component, component_method

from pig.components.behavior.Set_Attribute import Set_Attribute

class Spawned_Attribute( Set_Attribute):
    """When this object spawns another object, change an attribute on the
    spawned object."""
    #component_info
    _set = 'pig'
    _type = 'spawn'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['spawner_name', MyComponents, 
                    {'doc':'Name of the spawner component. '+\
                            'If blank, all spawners will be affected.'}]
            ]
    _field_list += Set_Attribute._field_list
    # defaults
    spawner_name = ""
    
    stripped_name = ""
    
    @component_method
    def on_added_to_scene(self, scene):
        "Over-ride Set_Component's auto-set. Just clean up spawner_name."
        # don't do the auto-set from Set_Component
        self.stripped_name = self.spawner_name.strip()
    
    @component_method                
    def on_spawn( self, obj, component):
        if not self.stripped_name or self.stripped_name == component.gname:
            Set_Attribute.do_change(self, obj)

register_component( Spawned_Attribute)