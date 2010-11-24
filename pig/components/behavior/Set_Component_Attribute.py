"Set_Component_Attribute.py"
from Opioid2D.public.Node import Node

from pug import MyComponents
from pug.component import *

from pig.components.behavior.Set_Attribute import Set_Attribute

class Set_Component_Attribute( Set_Attribute):
    """Change an attribute of one of owner's components when object is added to
scene. If multiple component's have the same name, they will all be altered."""
    # component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: 
      
    _field_list = [
            ['component_name', MyComponents,
                    {'doc':"The name of the component(s) to alter"}],
            ]
    _field_list += Set_Attribute._field_list
    
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
            list = self.owner.components.get()
            for component in list:
                if component.gname == self.component_name:
                    Set_Attribute.do_change(self, component)
        else:
            Set_Attribute.do_change(self, object)
            
register_component( Set_Component_Attribute)
        
       
