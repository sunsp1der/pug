###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
from pug_opioid.components.physics.Set_Rotation_Speed import \
        Set_Rotation_Speed
#######################
# End import autocode #
#######################

####################
# "fred3" autocode #
####################
class fred3(PugSprite):
    image = 'art/sprite.png'
    layer = 'bar'
    def on_create(self):
        self.gname = 'fred3'
        self.components.add( Set_Rotation_Speed(
                rotation_speed=80, ) )
        self.position.x = 600.0
        self.position.y = 200.0
        self.scale.x = 3.0
        self.scale.y = 1.0
########################
# End "fred3" autocode #
########################
