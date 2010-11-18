from Opioid2D import Delay, CallFunc
from Opioid2D.public.Node import Node

from pug.component import *

class Mouse_Click_Destroy( Component):
    """Object is destroyed when user clicks on it with mouse."""
    #component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['click','Destroy when mouse is clicked on object, ' +\
                       'then released. If false, destroy as soon'+\
                       'as mouse button is pressed on object.'],
            ['one_only','If true, other objects below this will not'+\
                        'register mouse clicks']
            ]
    
    #defaults
    click = True
    one_only = True

    @component_method
    def on_added_to_scene(self):
        "Register object for mouse clicks"
        if self.one_only:
            self.owner.mouse_register("single")
        else:
            self.owner.mouse_register("click")
        
    @component_method
    def on_click(self):
        "Destroy when clicked, if self.click is True"
        if self.click:
            self.owner.destroy()
            
    @component_method
    def on_press(self):
        "Destroy when pressed, if self.click is False"
        if not self.click:
            self.owner.destroy()
                
register_component( Mouse_Click_Destroy)
