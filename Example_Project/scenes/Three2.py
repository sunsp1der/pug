#################
# init autocode #
#################
from scenes.Three import Three
from scenes.pug_action_timing import TestSprite
#####################
# End init autocode #
#####################

#####################
# "Three2" autocode #
#####################
class Three2(Three):
    pass
    # Sprites etc.
    def enter(self):
        testsprite_instance = TestSprite()
        testsprite_instance.position.x = 400.3499755859375
        testsprite_instance.position.y = 300.0

        testsprite_instance_2 = TestSprite()
        testsprite_instance_2.position.x = 400.0
        testsprite_instance_2.position.y = 100.0

        testsprite_instance_3 = TestSprite()
        testsprite_instance_3.gname = 'orange'
        testsprite_instance_3.image_file = 'art/explosion2.png'
        testsprite_instance_3.rotation = 45.0
        testsprite_instance_3.position.x = 321.04998779296875
        testsprite_instance_3.position.y = 200.0
        testsprite_instance_3.scale.x = 10.0
        testsprite_instance_3.scale.y = 1.0

#########################
# End "Three2" autocode #
#########################
