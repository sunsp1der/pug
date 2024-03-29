### import autocode ###
from pig.Sprite import Sprite
from pug.all_components import Spawner
### End import autocode ###

### Launcher autocode ###
class Launcher(Sprite):
    image = 'art/pug.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 759.0
        self.position.y = 177.0
        self.color = (1.0, 0.0, 1.0, 1.0)
        self.rotation = 270.0
        self.components.add( Spawner(
                spawn_object='Target',
                spawn_offset=(0.5, 0)) )
### End Launcher autocode ###
