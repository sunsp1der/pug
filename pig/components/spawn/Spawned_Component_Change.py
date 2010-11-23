from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import register_component, component_method
from pug.gname import get_gnamed_object_list

from pig.components.spawn.Spawned_Attribute_Change import \
                                                    Spawned_Attribute_Change
from pig.components.behavior.Set_Attribute import Set_Attribute

class Spawned_Component_Change( Spawned_Attribute_Change):
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
    
    _component_name = ""

    @component_method
    def on_added_to_scene(self):
        "Clean up names."
        # don't do the auto-set from Set_Component
        if type(self.component_name) is str:
            self._component_name = self.component_name.strip()
        Spawned_Attribute_Change.on_added_to_scene(self)
    
    @component_method                
    def on_spawn( self, spawn_object, component):
        if not self._component_name:
            return
        if not self._spawner_name or self._spawner_name == component.gname:
            list = get_gnamed_object_list(self._component_name)
            for component in list:
                try:
                    owner = component.owner
                except:
                    continue
                if owner == spawn_object:
                    Set_Attribute.do_change(self, component)              

register_component( Spawned_Component_Change)