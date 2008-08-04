#################
# init autocode #
#################
from pug_opioid.PugSprite import PugSprite
#####################
# End init autocode #
#####################

###################
# "fred" autocode #
###################
class fred(PugSprite):
    image = 'art/sprite.png'
    layer = 'bar'
    def on_create(self):
        self.color = (0.0, 1.0, 0.0, 1.0)
        self.gname = 'fred'
        self.rotation = 236.0499267578125
        self.rotation_speed = 50.0
        self.position.x = 600.0
        self.position.y = 450.0
        self.scale.x = 30.0
        self.scale.y = 1.0
#######################
# End "fred" autocode #
#######################
