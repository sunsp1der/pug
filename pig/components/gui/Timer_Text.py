"Timer_Text.py"
from Opioid2D.public.Node import Node

from pug import Filename, Text
from pug.component import *

from pig.components import Value_Tracker_Text
from pig.util import get_gamedata

class Timer_Text(Value_Tracker_Text):
    "Show and update gamedata.timer"
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['prefix',Text,{'doc':'Display this before the time'}],
            ['start_time',"Starting value of timer, in seconds"],
            ['end_time',"Ending value of timer, in seconds"],
            ['interval','How often the timer is updated'],
            ['decimal_places',"Decimal places to show for seconds"],
            ]
    _field_list += Value_Tracker_Text._font_fields    
    #defaults
    __prefix = 'Time: '
    value_name = 'timer'
    decimal_places = 1
        
    @component_method
    def on_added_to_scene(self, scene):
        """Set score to zero unless otherwise set"""
        gamedata = get_gamedata()
        gamedata.register_callback( self.value_name, self.on_value_change)
        if getattr(gamedata, self.value_name, None) is None:
            setattr( gamedata, self.value_name, 0)
            
    def on_value_change(self, *a, **kw):
        self.set_text()            
            
    @component_method
    def set_text(self, text=None):
        "Show current value"
        gamedata = get_gamedata()
        if text is None:
            if getattr(gamedata, self.value_name, None) is None:
                text = self.prefix + self.default
            else:
                val = getattr(gamedata, self.value_name, self.default)
                if type(val) == float:
                    val =  ("%."+str(self.decimal_places)+"f") % val
                else:
                    val = str(val)
                text = self.prefix + val
        Textbox.set_text( self, text)
        
    def set_default(self, default):
        self.__default = default
        self.set_text()
    def get_default(self):
        return self.__default
    default = property(get_default, set_default)
    
    def set_prefix(self, prefix):
        self.__prefix = prefix
        self.set_text()
    def get_prefix(self):
        return self.__prefix
    prefix = property(get_prefix, set_prefix)            
                
        
register_component( Timer_Text)
