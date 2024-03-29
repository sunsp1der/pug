### import autocode ###
from pig.Sprite import Sprite
from pug.all_components import Spawner
### End import autocode ###

### SpawnWall autocode ###
class SpawnWall(Sprite):
    image = 'art/block.png'
    layer = 'walls'
    def on_create(self):
        self.position = (395.0, 424.0)
        self.scale = (100.0, 5.0)
        self.components.add( Spawner(
                spawn_object='Target',
                spawn_interval=3.0,
                spawn_interval_variance=2.0,
                spawn_location='top',
                obs_per_spawn_variance=1,
                max_spawns_in_scene=2) )
### End SpawnWall autocode ###
