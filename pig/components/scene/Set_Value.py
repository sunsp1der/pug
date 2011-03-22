from pug.component import *
from pug import Dropdown

from pig import Scene, get_gamedata
from pig import Director

class Set_Value( Component):
    """Set a gamedata value when scene starts."""
    # component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
        ['value_name','Name of the gamedata attribute to set'],
        ['value', 'Value to set it to'],
        ]
    #defaults
    value_name = 'enemies'
    value = 3
    
    @component_method
    def on_start(self):
        "Get and play the sound object"
        gamedata = get_gamedata()
        setattr(gamedata, self.value_name, self.value)
        
register_component( Set_Value)