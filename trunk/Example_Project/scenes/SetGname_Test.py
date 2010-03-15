"""SetGname_Test.py"""

### import autocode ###
from pug.all_components import Spawner
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

### "SetGname_Test" autocode ###
class SetGname_Test(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        PigSprite_instance = PigSprite()
        PigSprite_instance.image = 'art/pig.png'
        PigSprite_instance.layer = 'Background'
        PigSprite_instance.position.x = 388.0
        PigSprite_instance.position.y = 394.0
        PigSprite_instance.components.add( Spawner(
                object='RandFO') )

### End "SetGname_Test" autocode ###

