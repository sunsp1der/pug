###################
# import autocode #
###################
from scenes.pug_action_timing import TestSprite
#######################
# End import autocode #
#######################

#####################
# "Orange" autocode #
#####################
class Orange(TestSprite):
    image = 'art/explosion2.png'
    layer = 'foo'
    def on_create(self):
        self.rotation = 346.98550415039062
        self.rotation_speed = 30.0
        self.position.x = 200.0
        self.position.y = 200.0
        self.scale.x = 10.0
        self.scale.y = 1.0
#########################
# End "Orange" autocode #
#########################
