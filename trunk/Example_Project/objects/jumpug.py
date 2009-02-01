"""jumpug.py"""

###################
# import autocode #
###################
from all_components import Face_Object
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#####################
# "jumpug" autocode #
#####################
class jumpug(PugSprite):
    image = 'art/pug.png'
    layer = 'Layer 1'
    def on_create(self):
        self.position.x = 102.0
        self.position.y = 527.0
        self.color = (1.0, 1.0, 0.0, 1.0)
        self.register = True
        self.components.add( Face_Object(
                target='spawnero') )
        PugSprite.on_create(self)
#########################
# End "jumpug" autocode #
#########################

