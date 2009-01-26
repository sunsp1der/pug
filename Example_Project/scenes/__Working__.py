"""__Working__.py"""

###################
# import autocode #
###################
from all_components import Set_Motion, Follow_Mouse
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

####################
# "Three" autocode #
####################
class Three(PugScene):
    layers = ['sprite', 'two']
    def enter(self):
        # Sprites etc.
        pug = PugSprite(gname='pug')
        pug.components.add( Set_Motion(
                rotation_speed=100, ) )
        pug.image = 'art/pug.png'
        pug.layer = 'two'
        pug.position.x = 269.0
        pug.position.y = 423.0

        fellow = PugSprite(gname='fellow')
        fellow.color = (1.0, 0.0, 1.0, 1.0)
        fellow.components.add( Follow_Mouse() )
        fellow.image = 'art/pug.png'
        fellow.layer = 'two'
        fellow.position.x = 501.0
        fellow.position.y = 406.0

        # Pug auto-start
        self.start()
########################
# End "Three" autocode #
########################

