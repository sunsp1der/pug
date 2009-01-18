"""MyObjectClass2.py"""

###################
# import autocode #
###################
from all_components import Follow_Mouse, Set_Motion
from objects.Playa import Playa
#######################
# End import autocode #
#######################

#############################
# "MyObjectClass2" autocode #
#############################
class MyObjectClass2(Playa):
    def on_create(self):
        Playa.on_create(self)
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.position.x = 394.0
        self.position.y = 253.0
#################################
# End "MyObjectClass2" autocode #
#################################

