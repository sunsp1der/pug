"""Fadestar.py"""

###################
# import autocode #
###################
from all_components import Grow_Shrink, Self_Destruct
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#######################
# "Fadestar" autocode #
#######################
class Fadestar(PugSprite):
    image = 'art/explosion2.png'
    layer = 'Layer 1'
    def on_create(self):
        self.position.x = 701.0
        self.position.y = 126.0
#        self.components.add( Fade() )
        self.components.add( Grow_Shrink() )
        self.components.add( Self_Destruct() )
        PugSprite.on_create(self)
###########################
# End "Fadestar" autocode #
###########################

