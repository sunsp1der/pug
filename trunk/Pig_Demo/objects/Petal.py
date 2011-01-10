### import autocode ###
from pig.Sprite import Sprite
from pug.all_components import Grow_Shrink, Set_Motion, Self_Destruct
### End import autocode ###

### Petal autocode ###
class Petal(Sprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (568.0, 159.0)
        self.scale = (0.7, 0.7)
        self.tint = (128, 0, 255)
        self.components.add( Grow_Shrink(
                grow_in_secs=2.0,
                shrink_out_secs=2.0) )
        self.components.add( Set_Motion(
                velocity_y=-40,
                rotation_speed=30) )
        self.components.add( Self_Destruct(
                timer_secs=2.0) )
### End Petal autocode ###
