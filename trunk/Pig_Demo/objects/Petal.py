### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Grow_Shrink, Set_Motion, Self_Destruct
### End import autocode ###

### Petal autocode ###
class Petal(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (402.0, 127.0)
        self.tint = (128, 0, 255)
        self.components.add( Grow_Shrink(
                grow_in_secs=2.0,
                shrink_out_secs=2.0) )
        self.components.add( Set_Motion(
                velocity_y=-50,
                rotation_speed=30) )
        self.components.add( Self_Destruct(
                timer_secs=2.0) )
### End Petal autocode ###
