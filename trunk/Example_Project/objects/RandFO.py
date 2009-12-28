"""RandFO.py"""

###################
# import autocode #
###################
from pug.all_components import Random_Motion, Grow_Shrink, Life_Zone
from pig.PigSprite import PigSprite
#######################
# End import autocode #
#######################

#####################
# "RandFO" autocode #
#####################
class RandFO(PigSprite):
    image = 'art/ufo.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 229.0
        self.position.y = 155.0
        self.components.add( Random_Motion(
                velocity_min=50,
                velocity_max=200,
                align_rotation=False) )
        self.components.add( Grow_Shrink() )
        self.components.add( Life_Zone() )
#########################
# End "RandFO" autocode #
#########################

