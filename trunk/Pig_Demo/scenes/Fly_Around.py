### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, On_Start_Sound,\
    Key_Direction_Controls, Motion_Zone, Mouse_Face, Key_Spawn,\
    Collision_Destroy, On_Destroy_Sound, Spawn_On_Destroy, Spawner
### End import autocode ###

### Fly_Around autocode ###
class Fly_Around(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( Utility_Keys(
                info_F1='scenes\\Fly_Around_Help.txt') )
        self.components.add( On_Start_Sound(
                sound='sounds\\snap.wav') )

    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 400.0
        pigsprite_instance.position.y = 300.0
        pigsprite_instance.components.add( Key_Direction_Controls(
                x_velocity=200,
                y_velocity=200,
                rotate=False,
                up_key=119,
                down_key=115,
                left_key=97,
                right_key=100) )
        pigsprite_instance.components.add( Motion_Zone() )
        pigsprite_instance.components.add( Mouse_Face() )
        pigsprite_instance.components.add( Key_Spawn(
                key=1001,
                spawn_object='Bullet',
                spawn_offset=(0, -1),
                max_spawns_in_scene=1) )
        pigsprite_instance.components.add( Collision_Destroy(
                with_group='target',
                my_group='player') )
        pigsprite_instance.components.add( On_Destroy_Sound(
                sound='sounds\\snap.wav') )
        pigsprite_instance.components.add( Spawn_On_Destroy(
                spawn_object='ExplodeParticle',
                min_objects_per_spawn=15,
                max_objects_per_spawn=15,
                add_velocity=True) )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\block.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position.x = 400.0
        pigsprite_instance_2.position.y = 300.0
        pigsprite_instance_2.scale.x = 400.0
        pigsprite_instance_2.scale.y = 300.0
        pigsprite_instance_2.alpha = 0.0
        pigsprite_instance_2.components.add( Spawner(
                spawn_object='Target',
                spawn_interval=0.7,
                spawn_location='edges',
                max_objects_per_spawn=3,
                match_scale=False) )
### End Fly_Around autocode ###
