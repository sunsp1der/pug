### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Animate
### End import autocode ###

### Explosion autocode ###
class Explosion(PigSprite):
    layer = 'Background'
    def on_create(self):
        self.position = (156.0, 430.0)
        self.rotation = 180.0
        self.components.add( Animate(
                folder='art\\explosion',
                mode='Stop',
                destroy=True) )
### End Explosion autocode ###
