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
        self.position.x = 489.0
        self.position.y = 193.0
        self.scale.x = 0.30000001192092896
        self.scale.y = 0.30000001192092896
        self.color = (1.0, 0.0, 0.0, 1.0)
        self.components.add( Random_Motion(
                angle_min=-45,
                angle_max=45,
                velocity_min=75,
                velocity_max=125) )
        self.components.add( Set_Motion(
                acceleration_y=100,
                rotated=False) )
        self.components.add( Self_Destruct(
                timer_secs=2) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.2,
                shrink_out_secs=1.0) )
        self.components.add( Face_Motion() )
### End ExplodeParticle autocode ###
