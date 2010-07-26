### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

### testthisClass autocode ###
class testthisClass(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (314.0, 354.0)
### End testthisClass autocode ###
