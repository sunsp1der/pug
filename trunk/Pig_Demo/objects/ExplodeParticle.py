"""ExplodeParticle.py"""

### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Random_Motion, Set_Motion, Self_Destruct,\
    Grow_Shrink, Face_Motion
### End import autocode ###

### ExplodeParticle autocode ###
class ExplodeParticle(PigSprite):
    image = 'art\\pig.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 702.0
        self.position.y = 325.0
        self.scale.x = 0.30000001192092896
        self.scale.y = 0.30000001192092896
        self.tint = (1.0, 0.0, 0.0)
        self.components.add( Random_Motion(
                velocity_min=150,
                velocity_max=200) )
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
