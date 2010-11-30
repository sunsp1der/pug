### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Textbox, Set_Motion, Fade, Self_Destruct
### End import autocode ###

### LetterPetal autocode ###
class LetterPetal(PigSprite):
    layer = 'Background'
    def on_create(self):
        self.position = (569.0, 199.0)
        self.alpha = 0.5
        self.components.add( Textbox(
                gname='symbol',
                text='t',
                font_size=500,
                hotspot=(0.5, 0.5),
                cache_images=True) )
        self.components.add( Set_Motion(
                velocity_y=-200,
                acceleration_y=70,
                rotation_speed=40) )
        self.components.add( Fade() )
### End LetterPetal autocode ###
