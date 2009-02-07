"""YellowPug.py"""

###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

########################
# "YellowPug" autocode #
########################
class YellowPug(PugSprite):
    image = 'art/pug.png'
    layer = 'Layer 1'
    def on_create(self):
        self.position.x = 145.0
        self.position.y = 478.0
        self.color = (1.0, 1.0, 0.0, 1.0)
        PugSprite.on_create(self)
############################
# End "YellowPug" autocode #
############################

