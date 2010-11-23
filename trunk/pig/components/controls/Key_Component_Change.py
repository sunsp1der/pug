"Key_Component_Change.py"
from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import *
from pug.gname import get_gnamed_object_list

from pig.components.controls.Key_Attribute_Change import Key_Attribute_Change
from pig.components.behavior.Set_Attribute import Set_Attribute

class Key_Component_Change( Key_Attribute_Change):
    """Change an attribute of one of owner's components when key is pressed. If
multiple component's have the same name, they will all be altered."""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: 
      
    _field_list = [
            ['component_name', MyComponents,
                    {'doc':"The name of the component(s) to alter"}],
            ]
    _field_list += Key_Attribute_Change._field_list
    
    component_name = ""
    attribute = "enabled"
    change_value = False
    
    def do_change(self, object=None):
        """do_change(object=None): perform change defined by component
        
object: the object to be changed. In this case, the selected component.
"""
        if not self.component_name:
            return
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
            
register_component( Key_Component_Change)
        
       
