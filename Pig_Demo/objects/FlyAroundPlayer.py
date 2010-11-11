### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Key_Direction_Controls, Motion_Zone, Mouse_Face,\
    Key_Spawn, On_Destroy_Sound, Spawn_On_Destroy, Fade, Multiple_Lives,\
    Takes_Damage
### End import autocode ###

### FlyAroundPlayer autocode ###
class FlyAroundPlayer(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (405.0, 297.0)
        self.components.add( Key_Direction_Controls(
                x_velocity=200,
                y_velocity=200,
                rotate=False,
                up_key='W',
                down_key='S',
                left_key='A',
                right_key='D') )
        self.components.add( Motion_Zone() )
        self.components.add( Mouse_Face() )
        self.components.add( Key_Spawn(
                key=1001,
                spawn_object='Bullet',
                sound='sound\\beep.wav',
                spawn_offset=(0.5, 0),
                max_spawns_in_scene=1) )
        self.components.add( On_Destroy_Sound(
                sound='sound\\beep.wav') )
        self.components.add( Spawn_On_Destroy(
                spawn_object='ExplodeParticle',
                obs_per_spawn=15,
                obs_per_spawn_variance=5,
                add_velocity=True) )
        self.components.add( Fade(
                fade_in_secs=2.0,
                fade_out_secs=0.5) )
        self.components.add( Multiple_Lives(
                respawn_time=0.5,
                do_gameover=True) )
        self.components.add( Takes_Damage(
                invincible_time=2,
                value_name='health',
                group='player') )
### End FlyAroundPlayer autocode ###
