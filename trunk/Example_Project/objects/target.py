### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Collision_Destroy
### End import autocode ###

### target autocode ###
class target(PigSprite):
    image = 'art\\pig.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 656.0
        self.position.y = 432.0
        self.components.add( Collision_Destroy() )
### End target autocode ###
