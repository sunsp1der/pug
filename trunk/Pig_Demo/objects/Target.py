### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Collision_Destroy, Spawn_On_Destroy, Fade,\
    Grow_Shrink, Life_Zone, Random_Motion
### End import autocode ###

### Target autocode ###
class Target(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 706.0
        self.position.y = 266.0
        self.scale.x = 0.5
        self.scale.y = 0.5
        self.tint = (1.0, 0.0, 1.0)
        self.components.add( Collision_Destroy(
                with_group='bullet',
                my_group='target') )
        self.components.add( Spawn_On_Destroy(
                spawn_object='ExplodeParticle',
                min_objects_per_spawn=10,
                max_objects_per_spawn=20,
                add_velocity=True) )
        self.components.add( Fade(
                fade_in_secs=-1.0,
                fade_out_secs=0.3) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.6,
                shrink_out_secs=-1.0) )
        self.components.add( Life_Zone() )
        self.components.add( Random_Motion(
                angle_min=-30,
                angle_max=30,
                velocity_min=150,
                velocity_max=400) )
### End Target autocode ###
