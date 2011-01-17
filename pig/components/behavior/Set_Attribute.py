from copy import deepcopy
from weakref import proxy

from Opioid2D.public.Vector import VectorReference
from Opioid2D.public.Node import Node

from pug import Dropdown, Generic
from pug.component import *

from pig.components import SpriteComponent

class Set_Attribute(SpriteComponent):
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
                     'list':["=","+","*"],'sort':False}],                
        ['change_value', Generic,
                    {'doc':"Attribute will be changed by this value",
                     'do_typecast': False}],                     
        ]
    #defaults
    attribute = "scale"
    change_type = "="
    change_value = (2,2)
    
    @component_method
    def on_added_to_scene(self):
        """Set attribute when object is added to scene"""
        self.do_change()
        
    def do_change(self, object=None):
        """do_change(object=None): perform change defined by component
        
object: the object to be changed. This allows easy over-riding of this function
in derived components.
"""
        if object is None:
            object = self.owner
        value = getattr(object, self.attribute, None)
        original_value = value
        # make sure original_value is in proper format
        if original_value is value:
            # original was a reference
            try:
                original_value = deepcopy(value)
            except:
                # if we can't deepcopy, it's a special value
                try:
                    # take care of common use: VectorReference
                    if value.__class__ == VectorReference:
                        original_value = (value[0],value[1])
                except:
                    pass
        try:
            original_object = proxy(object)
        except:
            original_object = object
        try:
            # store info about how to undo change in undo_list
            # this allows multiple calls to do_change before undo is performed
            self.undo_list.append([original_object, self.attribute, 
                                   original_value])
        except:
            self.undo_list = [[original_object, self.attribute, original_value]]
        if self.change_type == "=":
            setattr(object, self.attribute, self.change_value)
        elif self.change_type == "+":
            setattr(object, self.attribute, 
                    value + self.change_value)
        elif self.change_type == "*":
            setattr(object, self.attribute, 
                    value * self.change_value)
            
    def undo_change(self):
        """undo_change(object=None): undo change defined by component
"""
        for unfo_info in self.undo_list:
            try:
                setattr(*unfo_info)
            except:
                pass
        self.undo_list = []
register_component( Set_Attribute)
