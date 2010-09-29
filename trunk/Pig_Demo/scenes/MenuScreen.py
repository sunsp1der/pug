### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Scene_Button, Textbox
### End import autocode ###

### MenuScreen autocode ###
class MenuScreen(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( Utility_Keys() )

    layers = ['Background', 'text']
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\block.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (417.0, 518.0)
        pigsprite_instance.scale = (50.0, 20.0)
        pigsprite_instance.components.add( Scene_Button(
                target='Dragon',
                hover_look=(165, 42, 42),
                hover_sound='sound\\beep.wav',
                click_sound='sound\\explosion.wav') )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.layer = 'text'
        pigsprite_instance_2.position = (380.0, 497.0)
        pigsprite_instance_2.tint = (0, 0, 0)
        pigsprite_instance_2.components.add( Textbox(
                text='dragon') )
### End MenuScreen autocode ###
