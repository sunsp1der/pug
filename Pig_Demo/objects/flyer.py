### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Key_Direction_Controls, Motion_Zone, Mouse_Face,\
    Key_Spawn, Collision_Destroy, On_Destroy_Sound, Spawn_On_Destroy
### End import autocode ###

### flyer autocode ###
class flyer(PigSprite):
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
                spawn_offset=(0, -1),
                max_spawns_in_scene=1) )
        self.components.add( Collision_Destroy(
                with_group='target',
                my_group='player') )
        self.components.add( On_Destroy_Sound(
                sound='sound\\snap.wav') )
        self.components.add( Spawn_On_Destroy(
                spawn_object='ExplodeParticle',
                obs_per_spawn=15,
                obs_per_spawn_variance=5,
                add_velocity=True) )
### End flyer autocode ###
