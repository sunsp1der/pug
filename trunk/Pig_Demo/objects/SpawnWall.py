### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Spawner
### End import autocode ###

### SpawnWall autocode ###
class SpawnWall(PigSprite):
    image = 'art\\block.png'
    layer = 'walls'
    def on_create(self):
        self.position.x = 394.0
        self.position.y = 413.0
        self.scale.x = 100.0
        self.scale.y = 5.0
        self.components.add( Spawner(
                spawn_object='Target',
                spawn_interval=4.0,
                spawn_location='top',
                obs_per_spawn_variance=1,
                max_spawns_in_scene=6,
                match_scale=False) )
### End SpawnWall autocode ###
