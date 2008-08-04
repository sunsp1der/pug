#################
# init autocode #
#################
from scenes.pug_action_timing import TimingScene, TestSprite
#####################
# End init autocode #
#####################

####################
# "Three" autocode #
####################
class Three(TimingScene):
    pass
    # Sprites etc.
    def enter(self):
        testsprite_instance = TestSprite()
        testsprite_instance.position.x = 400.3499755859375
        testsprite_instance.position.y = 300.0

        testsprite_instance_2 = TestSprite()
        testsprite_instance_2.position.x = 321.04998779296875
        testsprite_instance_2.position.y = 200.0

        testsprite_instance_3 = TestSprite()
        testsprite_instance_3.position.x = 400.0
        testsprite_instance_3.position.y = 100.0

########################
# End "Three" autocode #
########################
