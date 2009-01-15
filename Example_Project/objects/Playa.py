"""Playa.py"""

###################
# import autocode #
###################
from all_components import Follow_Mouse, Set_Motion
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

####################
# "Playa" autocode #
####################
class Playa(PugSprite):
    image = 'art/pug.png'
    layer = 'bar'
    def on_create(self,*args,**kwargs):
        self.color = (0.0, 0.0, 1.0, 1.0)
        self.gname = 'playa'
        self.components.add( Follow_Mouse() )
        self.components.add( Set_Motion(
                rotation_speed=25, ) )
        PugSprite.on_create(self,*args,**kwargs)
        self.position.x = 200.0
        self.position.y = 227.0
########################
# End "Playa" autocode #
########################

