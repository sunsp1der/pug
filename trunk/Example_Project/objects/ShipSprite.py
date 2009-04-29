"""ShipSprite.py"""

### import autocode ###
from pug_opioid.PugSprite import PugSprite
### End import autocode ###

### "ShipSprite" autocode ###
class ShipSprite(PugSprite):
    image = 'art/sprite.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 681.0
        self.position.y = 183.0
### End "ShipSprite" autocode ###

