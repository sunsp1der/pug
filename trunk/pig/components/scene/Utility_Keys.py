from Opioid2D import Director, Delay, CallFunc

from pug import Filename
from pug.component import *
from pug.util import start_file

from pig import PigScene
from pig.keyboard import *

class Utility_Keys( Component):
    """Add some basic utility keys to the scene"""
    # component_info
    _set = 'pig'
    _type = 'utilities'
    _class_list = [PigScene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['restart_ctrl_r', 'If True, ctrl-r restarts scene'],
            ['info_F1', Filename, {'doc':'Open this file if user presses F1'}],
            ]
    #defaults
    restart_ctrl_r = True
    info_F1 = None
    
    @component_method
    def on_start(self):
        self.k_info = self.owner.register_key_down( (keymods["CTRL"],keys["R"]),
                                                    self.do_restart)
        self.k_info = self.owner.register_key_down( keys["F1"],
                                                    self.do_info)
        
    @component_method
    def do_info(self):
        start_file( self.info_F1)
        
    @component_method
    def do_restart(self):
        Director.project_started = False
        (Delay(0)+CallFunc(Director.set_scene, Director.scene.__class__)).do()
        
        
register_component( Utility_Keys)