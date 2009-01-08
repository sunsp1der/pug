###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
from pug_opioid.components.physics.Set_Motion import Set_Motion
#######################
# End import autocode #
#######################

#####################
# "jumpug" autocode #
#####################
class jumpug(PugSprite):
    image = 'art/pug.png'
    layer = 'new_layer'
    def on_create(self, *args, **kwargs):
        self.gname = 'jumpug'
        self.components.add( Set_Motion(
                velocity_y=-400, 
                acceleration_y=200, 
                rotation_speed=1, ) )
        self.position.x = 102.0
        self.position.y = 527.0
#########################
# End "jumpug" autocode #
#########################
