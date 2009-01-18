"""MyObjectClass3.py"""

###################
# import autocode #
###################
from all_components import Follow_Mouse, Set_Motion
from objects.MyObjectClass2 import MyObjectClass2
#######################
# End import autocode #
#######################

#############################
# "MyObjectClass3" autocode #
#############################
class MyObjectClass3(MyObjectClass2):
    def on_create(self):
        MyObjectClass2.on_create(self)
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
#################################
# End "MyObjectClass3" autocode #
#################################

