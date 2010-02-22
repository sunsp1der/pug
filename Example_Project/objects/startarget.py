### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Collision_Destroy
### End import autocode ###

### startarget autocode ###
class startarget(PigSprite):
    image = 'art/explosion2.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 391.0
        self.position.y = 273.0
        self.components.add( Collision_Destroy(
                fromGroup='arp') )
### End startarget autocode ###
