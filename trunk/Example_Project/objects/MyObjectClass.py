"""MyObjectClass.py"""

###################
# import autocode #
###################
from objects.yellowpug import yellowpug
#######################
# End import autocode #
#######################

############################
# "MyObjectClass" autocode #
############################
class MyObjectClass(yellowpug):
    def on_create(self):
        yellowpug.on_create(self)
################################
# End "MyObjectClass" autocode #
################################

