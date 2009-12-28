"""test.py"""

### import autocode ###
from pug.all_components import Spawn_Area
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

### "test" autocode ###
class test(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        PigSprite_instance = PigSprite()
        PigSprite_instance.image = 'art/pug.png'
        PigSprite_instance.layer = 'Background'
        PigSprite_instance.position.x = 400.0
        PigSprite_instance.position.y = 300.0
        PigSprite_instance.components.add( Spawn_Area(
                object='UpFO',
                spawn_location='left') )
### End "test" autocode ###

