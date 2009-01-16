"""yellowpug.py"""

###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

########################
# "yellowpug" autocode #
########################
class yellowpug(PugSprite):
    image = 'art/pug.png'
    layer = 'bar'
    def on_create(self):
        PugSprite.on_create(self)
        self.color = (1.0, 1.0, 0.0, 1.0)
        self.rotation = 40.0
        self.position.x = 187.0
        self.position.y = 163.0
############################
# End "yellowpug" autocode #
############################

