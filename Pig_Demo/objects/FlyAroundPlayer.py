### import autocode ###
from pig.PigSprite import PigSprite
from pig.components.controls.Mouse_Face import Mouse_Face
from pug.all_components import Key_Direction_Controls, Motion_Zone, Key_Spawn,\
    On_Destroy_Sound, Spawn_On_Destroy, Fade, Multiple_Lives, Takes_Damage
### End import autocode ###

### FlyAroundPlayer autocode ###
class FlyAroundPlayer(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 300.0)
        self.components.add( Key_Direction_Controls(
                x_velocity=200,
                y_velocity=200,
                rotate=False,
                up_key=119,
                down_key=115,
                left_key=97,
                right_key=100) )
        self.components.add( Motion_Zone() )
        self.components.add( Mouse_Face() )
        self.components.add( Key_Spawn(
                key=1001,
                spawn_object='Bullet',
                sound='sound\\snap.wav',
                spawn_offset=(0, -1),
                max_spawns_in_scene=1) )
        self.components.add( On_Destroy_Sound(
                sound='sound\\snap.wav') )
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
