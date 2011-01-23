### import autocode ###
from pig.Sprite import Sprite
### End import autocode ###

### dummy autocode ###
class dummy(Sprite):
    image = 'art/pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 300.0)
### End dummy autocode ###
