"""FaceFollowMouse_Test.py"""

###################
# import autocode #
###################
from objects.ShipSprite import ShipSprite
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

###################################
# "FaceFollowMouse_Test" autocode #
###################################
class FaceFollowMouse_Test(PugScene):
    layers = ['Background', 'Layer 1']
    def enter(self):
        # Sprites
        pugsprite_instance = PugSprite()
        pugsprite_instance.register = True
        pugsprite_instance.image = 'art/pug.png'
        pugsprite_instance.layer = 'Background'
        pugsprite_instance.position.x = 376.0
        pugsprite_instance.position.y = 288.0

        shipsprite_instance = ShipSprite()
        shipsprite_instance.register = True

        # Pug auto-start
        self.start()
#######################################
# End "FaceFollowMouse_Test" autocode #
#######################################

