"""__Working__.py"""

###################
# import autocode #
###################
from objects.redfred import redfred
from objects.yellowpug import yellowpug
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

####################
# "Three" autocode #
####################
class Three(PugScene):
    layers = ['sprite', 'two', 'bar']
    def enter(self):
        # Sprites etc.
        explosion = PugSprite(gname='explosion')
        explosion.image = 'art/explosion2.png'
        explosion.layer = 'sprite'
        explosion.position.x = 400.0
        explosion.position.y = 100.0

        REF___tjis = PugSprite(gname='1REF$# tjis')
        REF___tjis.color = (1.0, 0.0, 1.0, 1.0)
        REF___tjis.image = 'art/pug.png'
        REF___tjis.layer = 'two'
        REF___tjis.position.x = 501.0
        REF___tjis.position.y = 406.0

        redfred_instance = redfred(gname='redfred')
        redfred_instance.archetype = True

        redfred_instance_2 = redfred()
        redfred_instance_2.position.x = 576.0
        redfred_instance_2.position.y = 270.0

        yellowpug_instance = yellowpug(gname='yellowpug')
        yellowpug_instance.archetype = True

        # Pug auto-start
        self.start()
########################
# End "Three" autocode #
########################

