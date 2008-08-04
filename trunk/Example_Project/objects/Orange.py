#################
# init autocode #
#################
from scenes.pug_action_timing import TestSprite
#####################
# End init autocode #
#####################

#####################
# "Orange" autocode #
#####################
class Orange(TestSprite):
    image = 'art/explosion2.png'
    layer = 'foo'
    def on_create(self):
        self._init_image = 'art/explosion2.png'
        self._init_layer = 'foo'
        self.rotation = 96.858932495117188
        self.rotation_speed = 30.0
        self.position.x = 200.0
        self.position.y = 200.0
        self.scale.x = 10.0
        self.scale.y = 1.0
#########################
# End "Orange" autocode #
#########################
