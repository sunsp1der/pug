### import autocode ###
from pig.Sprite import Sprite
from pug.all_components import Key_Drive_Controls, Key_Spawn
### End import autocode ###

### Cannon autocode ###
class Cannon(Sprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 514.0)
        self.opacity = 0.5
        self.components.add( Key_Drive_Controls(
                forward_key=None,
                backward_key=None) )
        self.components.add( Key_Spawn(
                spawn_object='Bullet',
                sound='sound\\beep.wav',
                spawn_offset=(0.5, 0),
                max_spawns_in_scene=1) )
### End Cannon autocode ###
