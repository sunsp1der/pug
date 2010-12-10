from Opioid2D import Director, Delay, CallFunc

from pygame import mixer

from pug import Filename
from pug.component import *
from pug.util import start_file

from pig import PigScene
from pig.keyboard import *
from pig.PigDirector import PigDirector

class Utility_Keys( Component):
    """Add some basic utility keys to the scene.
    
This adds new functions to the scene:
do_restart(): restarts scene (not game)
do_info(filename=None): try to open the filename with default program
volume_up()->current volume: raises volume
volume_down()->current volume: lowers volume
set_volume( volume)-> 0-1
toggle_mute(): mutes/unmutes sound
"""
    # component_info
    _set = 'pig'
    _type = 'utilities'
    _class_list = [PigScene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
            ['restart_ctrl_r', 'If True, ctrl-r restarts scene'],
            ['volume_up_ctrl_equal', 'If True, ctrl-= raises volume'],
            ['volume_down_ctrl_minus', 'If True, ctrl-- lowers volume'],
            ['mute_ctrl_zero', 'If True, ctrl-zero mutes/unmutes sound'],
            ['info_F1', Filename, {'doc':'Open this file if user presses F1'}],
            ]
    #defaults
    restart_ctrl_r = True
    volume_up_ctrl_equal = True
    volume_down_ctrl_minus = True
    mute_ctrl_zero = True
    info_F1 = None
    
    old_volume = volume = 1.0
    mute = False
    
    @component_method
    def on_start(self):
        "Register keys when scene starts"
        if self.restart_ctrl_r:
            self.owner.register_key_down( (keymods["CTRL"],keys["R"]),
                                                    self.do_restart,
                                                    _do_immediate=False)
        if self.volume_up_ctrl_equal:
            self.owner.register_key_down( (keymods["CTRL"],keys["EQUALS"]), 
                                          self.volume_up)
        if self.volume_down_ctrl_minus:
            self.owner.register_key_down( (keymods["CTRL"],keys["MINUS"]), 
                                          self.volume_down)
        if self.mute_ctrl_zero:
            self.owner.register_key_down( (keymods["CTRL"],keys["0"]), 
                                          self.toggle_mute)
        if self.info_F1:
            self.owner.register_key_down( keys["F1"], self.do_info)
                
    @component_method
    def do_info(self, filename=None):
        "do_info(filename=None): try to open the filename with default program"
        if filename is None:
            filename = self.info_F1
        try:
            start_file( filename)
        except:
            pass
        
    @component_method
    def set_volume(self, volume=None):
        "set_volume( volume): sets volume of all channels (0-1)"
        if volume is None:
            volume = self.volume
        else:
            self.volume = volume
        for i in range(mixer.get_num_channels()):
            mixer.Channel(i).set_volume(volume)

    @component_method
    def volume_up(self):
        "volume_up()->current volume: raises volume"
        self.volume += 0.1
        if self.volume > 1.0:
            self.volume = 1.0
        self.set_volume()
        
    @component_method
    def volume_down(self):
        "volume_down()->current volume: lowers volume"
        self.volume -= 0.1
        if self.volume < 0.0:
            self.volume = 1.0
        self.set_volume()
    
    @component_method
    def toggle_mute(self):
        "toggle_mute(): mutes sound"
        if self.volume:
            self.old_volume = self.volume
            self.volume = 0
            self.set_volume()
        else:
            self.volume = self.old_volume
            self.set_volume()
        
    @component_method
    def do_restart(self):
        "do_restart(): restart this scene (NOT the game itself)"
        #Director.project_started = False
        (Delay(0)+CallFunc(PigDirector.switch_scene_to,
                           PigDirector.scene.__class__)).do()
        
register_component( Utility_Keys)