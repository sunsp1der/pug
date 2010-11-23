### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Textbox, Set_Motion, Fade
### End import autocode ###

from pug.all_components import Fade

from pig.actions import *

### Pental autocode ###
class Pental(PigSprite):
    layer = 'Background'
    def on_create(self):
        self.position = (569.0, 199.0)
        self.alpha = 0.0
        self.components.add( Textbox(
                gname='symbol',
                text='t',
                font_size=500,
                hotspot=(0.5, 0.5)) )
        self.components.add( Set_Motion(
                velocity_y=-200,
                acceleration_y=70,
                rotation_speed=40) )
        self.components.add( Fade() )
### End Pental autocode ###

        self.components.add( Fade() )

#
#    def on_added_to_scene(self):
#        self.do( action)
#
#action =    Repeat((
#                    ColorFade((0,0,1,0.5),1) + \
#                    ColorFade((0,1,0,0.5),1) + \
#                    ColorFade((1,0,0,0.5),1)),
#                5) + \
#            Delete()
