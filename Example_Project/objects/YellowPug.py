"""YellowPug.py"""

### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

### YellowPug autocode ###
class YellowPug(PigSprite):
    image = 'art/pug.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 145.0
        self.position.y = 478.0
        self.color = (1.0, 0.0, 0.0, 1.0)
### End YellowPug autocode ###
