"""MousePick2.py"""

###################
# import autocode #
###################
from all_components import Follow_Mouse, Set_Motion
from objects.Playa import Playa
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

#########################
# "MousePick2" autocode #
#########################
class MousePick2(PugScene):
    layers = ['bar']
    def enter(self):
        # Sprites etc.
        playa = Playa(gname='playa')
        playa.components.add( Follow_Mouse() )
        playa.components.add( Set_Motion(
                rotation_speed=25, ) )
        playa.position.x = 394.0
        playa.position.y = 253.0

        # Pug auto-start
        self.start()
#############################
# End "MousePick2" autocode #
#############################

