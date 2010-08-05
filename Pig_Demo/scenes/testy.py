### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import On_Key_Sound_Scene, On_Start_Sound, Textbox
### End import autocode ###

### testy autocode ###
class testy(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( On_Key_Sound_Scene(
                sound='sound\\pickup.wav',
                fade_out=1) )
        self.components.add( On_Start_Sound(
                sound='sound\\snap.wav',
                fade_out=1) )

    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.components.add( Textbox(
                text='texeeeee awoioiedoide',
                max_width=50) )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (386.0, 277.0)
        pigsprite_instance_2.components.add( Textbox(
                text='texeeeee') )
        
### End testy autocode ###
