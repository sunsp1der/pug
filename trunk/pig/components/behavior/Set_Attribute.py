from copy import deepcopy

from Opioid2D.public.Vector import VectorReference
from Opioid2D.public.Node import Node

from pug import Dropdown, Generic
from pug.component import *

class Set_Attribute(Component):
    "When owner is added to scene, an attribute is set to a given value."
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
        ['attribute',"Owner's attribute to set"],
        ['change_type', Dropdown,
                    {'doc':"Attribute will be changed in this way",
                     'list':["=","+","*"]}],                
        ['change_value', Generic,
                    {'doc':"Attribute will be changed by this value",
                     'do_typecast': False}],                     
        ]
    #defaults
    attribute = "scale"
    change_type = "="
    change_value = (2,2)
    
    original_value = None
    original_object = None
        
    @component_method
    def on_added_to_scene(self, scene):
        """Set attribute when object is added to scene"""
        self.do_change()
        
    def do_change(self, object=None):
        """do_change(object=None): perform change defined by component
        
object: the object to be changed. This allows easy over-riding of this function
in derived components.
"""
        if object is None:
            object = self.owner
        value = getattr(object, self.attribute)
        if self.original_value is None:
            self.original_value = value
            if self.original_value is value:
                # original was a reference
                try:
                    self.original_value = deepcopy(value)
                except:
                    # if we can't deepcopy, it's a special value
                    try:
                        # take care of common use: VectorReference
                        if value.__class__ == VectorReference:
                            self.original_value = (value[0],value[1])
                    except:
                        pass
        self.original_object = object
        if self.change_type == "=":
            setattr(object, self.attribute, self.change_value)
        elif self.change_type == "+":
            setattr(object, self.attribute, 
                    value + self.change_value)
        elif self.change_type == "*":
            setattr(object, self.attribute, 
                    value * self.change_value)
            
    def undo_change(self, object=None):
        """undo_change(object=None): undo change defined by component
        
object: the object to be changed. This allows easy over-riding of this function
in derived components.
"""
        if not self.key_up_undo:
            return
        if object is None:
            object = self.original_object
        print self.attribute, self.original_value
        setattr(object, self.attribute, self.original_value)
        self.original_value = None
register_component( Set_Attribute)
