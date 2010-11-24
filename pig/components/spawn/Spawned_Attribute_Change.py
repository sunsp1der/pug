from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import Component, register_component, component_method

from pig.components.behavior.Set_Attribute import Set_Attribute

class Spawned_Attribute_Change( Set_Attribute):
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
    _spawner_name = ""
    
    @component_method
    def on_added_to_scene(self):
        "Over-ride Set_Component's auto-set."
        # don't do the auto-set from Set_Component
        pass
    
    @component_method                
    def on_spawn( self, obj, component):
        if not self._spawner_name or self._spawner_name == component.gname:
            Set_Attribute.do_change(self, obj)
            
    def get_spawner_name(self):
        return self._spawner_name
    def set_spawner_name(self, name):
        self._spawner_name = name.strip()
    spawner_name = property(get_spawner_name, set_spawner_name)

register_component( Spawned_Attribute_Change)