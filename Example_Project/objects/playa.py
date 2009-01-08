###################
# import autocode #
###################
from all_components import Follow_Mouse, Set_Motion
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

####################
# "playa" autocode #
####################
class playa(PugSprite):
    image = 'art/pug.png'
    layer = 'bar'
    def on_create(self):
        self.gname = 'playa'
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.position.x = 430.0
        self.position.y = 419.0
########################
# End "playa" autocode #
########################
