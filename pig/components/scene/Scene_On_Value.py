from pug.component import *
from pug import Dropdown

from pig import Scene, get_gamedata
from pig.editor.agui import ScenesDropdown
from pig import Director

class Scene_On_Value( Component):
    """Change to another scene when a gamedata attribute reaches a certain
value."""
    # component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
        ['scene',ScenesDropdown,{'doc':'Scene to switch to', 
                                 'component':True }],                   
        ['value_name','The name of the gamedata attribute to check.'],
        ['test_type', Dropdown, {'doc':'How to check the value',
                                 'list':['=','>','<','>=','<='],
                                 'sort':False}],
        ['test_value', 'Compare the value to this using test_type'],
        ['relative_to_start', 'Add the starting value to test_value'+\
                ' to get the actual value to test against.']
        ]
    #defaults
    scene = None
    value_name = 'score'
    test_type = '='
    test_value = 100
    relative_to_start = True
    
    @component_method
    def on_start(self):
        "Get and play the sound object"
        gamedata = get_gamedata()
        if self.relative_to_start:
            self.test_value += getattr(gamedata, self.value_name)
        gamedata.register_callback(self.value_name, self.on_value_change)        
        
    @component_method
    def on_exit(self):
        "Stop the sound"
        gamedata = get_gamedata()
        gamedata.unregister_callback(self.value_name, self.on_value_change)
        
    def on_value_change(self, value, attr, gamedata):
        change_scene = False
        if self.test_type == '=':
            if value == self.test_value:
                change_scene = True
        elif self.test_type == '>':
            if value > self.test_value:
                change_scene = True
        elif self.test_type == '<':
            if value < self.test_value:
                change_scene = True
        elif self.test_type == '>=':
            if value >= self.test_value:
                change_scene = True
        elif self.test_type == '<=':
            if value <= self.test_value:
                change_scene = True
        if change_scene:
            Director.switch_scene_to(self.scene)
        
        
register_component( Scene_On_Value)