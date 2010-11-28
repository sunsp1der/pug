### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

### dummy autocode ###
class dummy(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 300.0)
### End dummy autocode ###
