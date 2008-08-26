###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

###################
# "fred" autocode #
###################
class fred(PugSprite):
    image = 'art/sprite.png'
    layer = 'bar'
    def on_create(self):
        self.gname = 'fred'
        self.components.add( Set_Rotation_Speed(
                rotation_speed=33, ) )
        self.position.x = 600.0
        self.position.y = 450.0
        self.scale.x = 3.0
        self.scale.y = 1.0
#######################
# End "fred" autocode #
#######################
