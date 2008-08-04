#################
# init autocode #
#################
from scenes.Three import Three
from scenes.pug_action_timing import TestSprite
#####################
# End init autocode #
#####################

#####################
# "Three3" autocode #
#####################
class Three3(Three):
    pass
    # Sprites etc.
    def enter(self):
        testsprite_instance = TestSprite()
        testsprite_instance.color = (1.0, 0.0, 1.0, 1.0)
        testsprite_instance.rotation = 260.00759887695312
        testsprite_instance.rotation_speed = 20.0
        testsprite_instance.position.x = 321.04998779296875
        testsprite_instance.position.y = 400.0
        testsprite_instance.scale.x = 3.0
        testsprite_instance.scale.y = 3.0

        testsprite_instance_2 = TestSprite()
        testsprite_instance_2.position.x = 400.3499755859375
        testsprite_instance_2.position.y = 300.0

        testsprite_instance_3 = TestSprite()
        testsprite_instance_3.position.x = 400.0
        testsprite_instance_3.position.y = 100.0

#########################
# End "Three3" autocode #
#########################
