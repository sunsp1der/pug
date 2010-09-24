### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Spawn_On_Destroy, Fade, Grow_Shrink, Life_Zone,\
    Score_On_Destroy, Deals_Damage, Takes_Damage, On_Damage_Sound,\
    Random_Motion
### End import autocode ###

### Target autocode ###
class Target(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (213.0, 382.0)
        self.scale = (0.5, 0.5)
        self.tint = (255, 0, 128)
        self.components.add( Spawn_On_Destroy(
                spawn_object='ExplodeParticle',
                obs_per_spawn=4,
                obs_per_spawn_variance=1,
                add_velocity=True) )
        self.components.add( Fade(
                fade_in_secs=-1.0,
                fade_out_secs=0.3) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.6,
                shrink_out_secs=-1.0) )
        self.components.add( Life_Zone() )
        self.components.add( Score_On_Destroy() )
        self.components.add( Deals_Damage(
                damage_amount=50.0,
                with_group='player',
                my_group='target') )
        self.components.add( Takes_Damage(
                start_health=10.0,
                invincible_time=0,
                group='target') )
        self.components.add( On_Damage_Sound(
                sound='sound\\explosion.wav') )
        self.components.add( Random_Motion(
                angle_min=-30,
                angle_max=30,
                velocity_min=150,
                velocity_max=400) )
        self.components.add( Spawn_On_Destroy(
                spawn_object='Explosion',
                add_velocity=True) )
### End Target autocode ###
