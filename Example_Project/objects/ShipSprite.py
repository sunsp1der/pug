"""ShipSprite.py"""

###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#########################
# "ShipSprite" autocode #
#########################
class ShipSprite(PugSprite):
    image = 'art/sprite.png'
    layer = 'Layer 1'
    def on_create(self):
        self.position.x = 681.0
        self.position.y = 183.0
        PugSprite.on_create(self)
#############################
# End "ShipSprite" autocode #
#############################

