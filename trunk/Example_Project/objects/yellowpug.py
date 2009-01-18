"""yellowpug.py"""

###################
# import autocode #
###################
from objects.MyObjectClass import MyObjectClass
#######################
# End import autocode #
#######################

########################
# "yellowpug" autocode #
########################
class yellowpug(MyObjectClass):
    def on_create(self):
        MyObjectClass.on_create(self)
        self.position.x = 434.0
        self.position.y = 287.0
############################
# End "yellowpug" autocode #
############################

