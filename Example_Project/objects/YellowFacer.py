"""YellowFacer.py"""

###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

##########################
# "YellowFacer" autocode #
##########################
class YellowFacer(PugSprite):
    image = 'art/pug.png'
    layer = 'Layer 1'
    def on_create(self):
        self.position.x = 416.0
        self.position.y = 322.0
        self.color = (1.0, 1.0, 0.0, 1.0)
        PugSprite.on_create(self)
##############################
# End "YellowFacer" autocode #
##############################

