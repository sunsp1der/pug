"Key_Component_Change.py"
from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import *
from pug.gname import get_gnamed_object_list

from pig.components.controls.Key_Attribute_Change import Key_Attribute_Change
from pig.components.behavior.Set_Component_Attribute \
                                        import Set_Component_Attribute

class Key_Component_Change( Key_Attribute_Change, Set_Component_Attribute):
    """Change an attribute of one of owner's components when key is pressed. If
multiple component's have the same name, they will all be altered."""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: 
      
    _field_list = []
    _field_list += Key_Attribute_Change._key_list
    _field_list += Set_Component_Attribute._field_list
    
    component_name = ""
    attribute = "enabled"
    change_value = False
            
register_component( Key_Component_Change)
        
       
