"""jumpug.py"""

###################
# import autocode #
###################
from all_components import Face_Object, Forward_Motion
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#####################
# "jumpug" autocode #
#####################
class jumpug(PugSprite):
    image = 'art/pug.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 106.0
        self.position.y = 442.0
        self.color = (1.0, 1.0, 0.0, 1.0)
        self.register = True
        self.components.add( Face_Object(
                target='spawnero',
                rotation_speed=100) )
        self.components.add( Forward_Motion(
                ) )
        PugSprite.on_create(self)
#########################
# End "jumpug" autocode #
#########################

