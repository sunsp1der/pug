### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Grow_Shrink
### End import autocode ###

### mulitplier autocode ###
class mulitplier(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (320.0, 364.0)
        self.components.add( Grow_Shrink(
                gname='grow1') )
        self.components.add( Grow_Shrink() )
### End mulitplier autocode ###
