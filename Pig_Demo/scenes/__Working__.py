### import autocode ###
from objects.SpawnWall import SpawnWall
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Fade, Collision_Destroy, Grow_Shrink,\
    Key_Drive_Controls, Join_Collision_Group, Spawner
### End import autocode ###

### FadeTest autocode ###
class FadeTest(PigScene):
    layers = ['Background', 'walls']
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.components.add( Fade(
                fade_in_secs=0.0) )
        pigsprite_instance.components.add( Collision_Destroy() )
        pigsprite_instance.components.add( Grow_Shrink(
                shrink_out_secs=0.0) )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (398.0, 387.0)
        pigsprite_instance_2.components.add( Key_Drive_Controls() )
        pigsprite_instance_2.components.add( Join_Collision_Group() )

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.image = 'art\\pug.png'
        pigsprite_instance_3.layer = 'Background'
        pigsprite_instance_3.position = (410.0, 310.0)

        spawnwall_instance = SpawnWall()
        spawnwall_instance.position = (201.0, 316.0)
        spawnwall_instance.rotation = 45.0
        spawnwall_instance.tint = (0.0, 0.0, 0.50196081399917603)
        spawnwall_instance.components.add( Spawner(
                spawn_object='Target',
                spawn_interval=4.0,
                spawn_location='area',
                obs_per_spawn_variance=1,
                max_spawns_in_scene=6,
                match_scale=False) )
        spawnwall_instance.components.remove_duplicate_of( Spawner(
                spawn_object='Target',
                spawn_interval=4.0,
                spawn_location='top',
                obs_per_spawn_variance=1,
                max_spawns_in_scene=6,
                match_scale=False) )
### End FadeTest autocode ###
