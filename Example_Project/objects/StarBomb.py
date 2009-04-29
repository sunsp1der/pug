"""StarBomb.py"""

### import autocode ###
from all_components import Spawn_On_Destroy, Self_Destruct, Fade, \
        Random_Motion, \
        Grow_Shrink
from pug_opioid.PugSprite import PugSprite
### End import autocode ###

### "StarBomb" autocode ###
class StarBomb(PugSprite):
    image = 'art/ball.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 400.0
        self.position.y = 300.0
        self.components.add( Spawn_On_Destroy(
                object='ExplodeParticle',
                min_objects_per_spawn=10,
                max_objects_per_spawn=20) )
        self.components.add( Self_Destruct() )
        self.components.add( Fade(
                fade_in_secs=-1,
                fade_out_secs=0.29999999999999999) )
        self.components.add( Random_Motion(
                angle_min=-45,
                angle_max=45,
                velocity_min=50,
                velocity_max=120) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.5,
                shrink_out_secs=-1) )
### End "StarBomb" autocode ###

