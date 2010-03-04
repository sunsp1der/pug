"""YellowFacer.py"""

###################
# import autocode #
###################
from pug.all_components import Mouse_Face
from pig.PigSprite import PigSprite
#######################
# End import autocode #
#######################

##########################
# "YellowFacer" autocode #
##########################
class YellowFacer(PigSprite):
    image = 'art/pig.png'
    layer = 'Layer 1'
    def on_create(self):
        self.position.x = 416.0
        self.position.y = 322.0
        self.color = (1.0, 1.0, 0.0, 1.0)
        self.components.add( Mouse_Face() )
        PigSprite.on_create(self)
##############################
# End "YellowFacer" autocode #
##############################

