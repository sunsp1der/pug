"Value_Tracker_Text.py"
from Opioid2D.public.Node import Node

from pug import Text
from pug.component import *

from pig.components import Textbox
from pig.util import get_gamedata

class Value_Tracker_Text(Textbox):
    "Show a value from gamedata"
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['prefix',Text,{
                'doc':'Display this before the value'}],
            ['value_name',Text,{'doc':'Name of gamedata attribute to track'}],
            ['start_value',"Value when project starts"],
            ['decimal_places',"If value is a number, show this\n"+\
                                "many decimal places"],
            ['default',Text,{'doc:':'Text to display in editor\n'+\
                             '(prefix added automatically)'}],
            ]
    _field_list += Textbox._font_fields
    #defaults
    _default = '000'
    _prefix = 'Score: '
    value_name = 'score'
    decimal_places = 0
    start_value = 0
                
    @component_method
    def on_added_to_scene(self, scene):
        """Set score to zero unless otherwise set"""
        gamedata = get_gamedata()
        try:
            getattr(gamedata, self.value_name)
        except:
            setattr( gamedata, self.value_name, self.start_value)            
        gamedata.register_callback( self.value_name, self.on_value_change)
        self.set_text()
            
    @component_method
    def on_destroy(self):
        gamedata = get_gamedata()
        gamedata.unregister_callback(self.value_name, self.on_value_change)

    def on_value_change(self, *a, **kw):
        self.set_text()
        print "********",a,kw
            
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
        self._default = default
        self.set_text()
    def get_default(self):
        return self._default
    default = property(get_default, set_default)
    
    def set_prefix(self, prefix):
        self._prefix = prefix
        self.set_text()
    def get_prefix(self):
        return self._prefix
    prefix = property(get_prefix, set_prefix)            
                
        
register_component( Value_Tracker_Text)
