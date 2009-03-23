"""SetGname_Test.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

############################
# "SetGname_Test" autocode #
############################
class SetGname_Test(PugScene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        pugsprite_instance = PugSprite()
        pugsprite_instance.image = 'art/pug.png'
        pugsprite_instance.layer = 'Background'
        pugsprite_instance.position.x = 388.0
        pugsprite_instance.position.y = 394.0
        pugsprite_instance.components.add( Spawn_Area(
                object='RandFO') )

################################
# End "SetGname_Test" autocode #
################################

