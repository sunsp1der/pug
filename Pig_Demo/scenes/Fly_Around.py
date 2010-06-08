### import autocode ###
from objects.SpawnWall import SpawnWall
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
                sound='sound\\snap.wav') )

    def on_enter(self):
        # Archetypes
        SpawnWall_archetype = SpawnWall(gname='SpawnWall')
        SpawnWall_archetype.archetype = True

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
                sound='sound\\snap.wav') )
        pigsprite_instance.components.add( Spawn_On_Destroy(
                spawn_object='ExplodeParticle',
                obs_per_spawn = 15,
                obs_per_spawn_variance = 5,
                add_velocity=True) )

### End Fly_Around autocode ###
