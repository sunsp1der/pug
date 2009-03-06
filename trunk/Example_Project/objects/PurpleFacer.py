"""PurpleFacer.py"""

###################
# import autocode #
###################
from all_components import Face_Mouse
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

##########################
# "PurpleFacer" autocode #
##########################
class PurpleFacer(PugSprite):
    image = 'art/pug.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 541.0
        self.position.y = 389.0
        self.color = (0.69999998807907104, 0.0, 1.0, 1.0)
        self.components.add( Face_Mouse() )
        PugSprite.on_create(self)
##############################
# End "PurpleFacer" autocode #
##############################

