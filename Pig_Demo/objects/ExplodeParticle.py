"""ExplodeParticle.py"""

### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Random_Motion, Set_Motion, Self_Destruct,\
    Grow_Shrink, Face_Motion
### End import autocode ###

### ExplodeParticle autocode ###
class ExplodeParticle(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (702.0, 325.0)
        self.scale = (0.3, 0.3)
        self.tint = (255, 0, 0)
        self.components.add( Random_Motion(
                velocity=175,
                velocity_variance=25) )
        self.components.add( Set_Motion(
                acceleration_y=200,
                rotated=False) )
        self.components.add( Self_Destruct(
                timer_secs=0.5) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.1,
                shrink_out_secs=0.5) )
        self.components.add( Face_Motion() )
### End ExplodeParticle autocode ###
