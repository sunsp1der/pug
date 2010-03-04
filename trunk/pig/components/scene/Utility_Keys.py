from Opioid2D import Director

from pig import PigScene

from pug.component import *

from pig.keyboard import *

class Utility_Keys( Component):
    """Add some basic utility keys to the scene"""
    # component_info
    _set = 'pig'
    _type = 'controls'
    _class_list = [PigScene]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['restart_ctrl_r', 'If True, ctrl-r restarts scene'],
            ]
    #defaults
    restart_ctrl_r = True
    
    @component_method
    def on_enter(self):
        self.k_info = self.owner.register_key_down( (keymods["CTRL"],keys["R"]),
                                                    self.restart)
        
    def restart(self):
        Director.game_started = False
        Director.set_scene( Director.scene.__class__)
        
        
register_component( Utility_Keys)