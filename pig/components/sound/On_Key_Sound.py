from Opioid2D.public.Node import Node

from pug.component import *

from pig.editor.agui import KeyDropdown, SoundFile
from pig.audio import get_sound
from pig.keyboard import keys
from pig.PigDirector import PigDirector
from pig.components import SpriteComponent

class On_Key_Sound( SpriteComponent):
    """Owner plays a sound when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = [
        ["key", KeyDropdown, {'doc':"The key that triggers the sound"}],
        ["sound", SoundFile, {'doc':"The sound to play"}],
        ["loops", "Number of extra times to loop sound.\n"+\
                    "-1 continues until key is released."],
        ["fade_in", "Number of seconds to take fading in the sound"],
        ["fade_out", "Number of seconds to take fading out the sound"]
        ]
    key = keys["S"]
    sound = None
    loops = 0
    fade_in = 0
    fade_out = 0
    
    sound_object = None
    play_channel = None
    
    @component_method
    def on_added_to_scene(self):
        "Get the sound object and set it to play when key is pressed"
        self.setup()
        
    def setup(self):
        scene = PigDirector.scene #@UndefinedVariable
        self.sound_object = get_sound( self.sound)
        if self.key:
            self.kinfo = scene.register_key_down(self.key, self.play)
            self.kinfo2 = scene.register_key_up(self.key, self.stop)

    def play(self):
        try:
            self.play_channel = self.sound_object.play(loops=self.loops, 
                                            fade_ms=int(self.fade_in*1000))
        except:
            pass
        
    def stop(self):
        if self.play_channel:
            self.play_channel.fadeout(int(self.fade_out*1000))
        self.play_channel=None

    @component_method
    def on_destroy(self):
        "Unregister key"
        self.unregister_keys()
        
    def unregister_keys(self):
        try:
            PigDirector.scene.unregister_key(self.kinfo) #@UndefinedVariable
            PigDirector.scene.unregister_key(self.kinfo2) #@UndefinedVariable
        except:
            pass
    
register_component( On_Key_Sound)
    