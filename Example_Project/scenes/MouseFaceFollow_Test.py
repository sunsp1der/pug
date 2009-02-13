"""MouseFaceFollow_Test.py"""

###################
# import autocode #
###################
from all_components import Follow_Mouse, Face_Object, Face_Mouse
from objects.ShipSprite import ShipSprite
from objects.YellowPug import YellowPug
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

###################################
# "MouseFaceFollow_Test" autocode #
###################################
class MouseFaceFollow_Test(PugScene):
    layers = ['Background']
    def enter(self):
        # Archetypes
        YellowPug_archetype = YellowPug(gname='YellowPug')
        YellowPug_archetype.archetype = True

        # Sprites
        shipsprite_instance = ShipSprite()
        shipsprite_instance.components.add( Follow_Mouse() )
        shipsprite_instance.components.add( Face_Object(
                target='mouse pointer',
                offset=-90) )

        mouse_pointer = YellowPug(gname='mouse pointer')
        mouse_pointer.position.x = 436.0
        mouse_pointer.position.y = 247.0
        mouse_pointer.components.add( Face_Mouse() )

        # Pug auto-start
        self.start()
#######################################
# End "MouseFaceFollow_Test" autocode #
#######################################

