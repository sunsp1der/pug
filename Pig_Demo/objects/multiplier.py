### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Random_Motion, Key_Spawn, Life_Zone
### End import autocode ###

### multiplier autocode ###
class multiplier(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (200.0, 411.0)
        self.components.add( Random_Motion() )
        self.components.add( Key_Spawn(
                key=97,
                spawn_object='Bullet') )
        self.components.add( Life_Zone() )
### End multiplier autocode ###
