#################
# init autocode #
#################
from Orange import Orange
#####################
# End init autocode #
#####################

#########################
# "orangespin" autocode #
#########################
class orangespin(Orange):
    image = 'art/explosion2.png'
    layer = 'fork'
    def on_create(self):
        self.position.x = 321.04998779296875
        self.position.y = 200.0
        self.scale.x = 10.0
        self.scale.y = 1.0
        self.gname = 'orange'
        self.rotation_speed = 50.0
#############################
# End "orangespin" autocode #
#############################
