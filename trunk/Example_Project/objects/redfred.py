"""redfred.py"""

###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

######################
# "redfred" autocode #
######################
class redfred(PugSprite):
    image = 'art/sprite.png'
    layer = 'bar'
    def on_create(self):
        PugSprite.on_create(self)
        self.color = (1.0, 0.0, 0.0, 1.0)
        self.rotation = 40.0
        self.position.x = 112.0
        self.position.y = 442.0
        self.scale.x = 2.0
        self.scale.y = 2.0
##########################
# End "redfred" autocode #
##########################

