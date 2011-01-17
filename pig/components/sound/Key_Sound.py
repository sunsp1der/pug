from Opioid2D.public.Node import Node

from pug.component import *

from pig.editor.agui import KeyDropdown
from pig.keyboard import keys
from pig.PigDirector import PigDirector
from pig.components.sound.On_Create_Sound import On_Create_Sound

class Key_Sound( On_Create_Sound):
    """Owner plays a sound when key is pressed"""
    # component_info
    _set = 'pig'
    _type = 'sound'
    _class_list = [Node]
    # attributes:   
    _field_list = []
    _field_list += On_Create_Sound._field_list
    _field_list += [
        ["key", KeyDropdown, {'doc':"The key that triggers the sound"}],
        ["key_up_stop","Stop playing the sound when key is released"],
    ]
    _loop_fields = [ 
        ["loops", "Number of extra times to loop sound.\n"+\
                    "-1 continues until key is released."],
        ["fade_in", "Number of seconds to take fading in the sound"],
        ["fade_out", "Number of seconds to take fading out the sound"]
        ]
    _field_list += _loop_fields
    #defaults
    key = keys["S"]
    key_up_stop = False
    loops = 0
    fade_in = 0
    fade_out = 0
    
    play_channel = None
    
    @component_method
    def on_added_to_scene(self):
        "Set up the sound object"
        self.setup()
    
    def setup(self):
        "setup(): Set up the sound. This is for ease of derivation."
        On_Create_Sound.setup(self)
        if self.key:
            scene = PigDirector.scene
            self.kinfo = scene.register_key_down(self.key, self.play)
            self.kinfo2 = scene.register_key_up(self.key, self.stop)

    def play(self):
        try:
            self.play_channel = self.sound_object.play(loops=self.loops, 
                                            fade_ms=int(self.fade_in*1000))
#            print self.play_channel, self.sound_object
#            import threading
#            print 'sceneplay', threading.currentThread()

        except:
            pass
        
    def stop(self):
        if not self.key_up_stop:
            return
        if self.play_channel and \
                            self.play_channel.get_sound == self.sound_object:
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
    
register_component( Key_Sound)
    