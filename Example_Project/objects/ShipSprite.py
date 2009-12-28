"""ShipSprite.py"""

### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

### "ShipSprite" autocode ###
class ShipSprite(PigSprite):
    image = 'art/sprite.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 681.0
        self.position.y = 183.0
### End "ShipSprite" autocode ###

