"""Three.py"""

###################
# import autocode #
###################
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
        ship = PugSprite(gname='ship')
        ship.image = 'art/sprite.png'
        ship.layer = 'sprite'
        ship.position.x = 402.0
        ship.position.y = 100.0

        explosion = PugSprite(gname='explosion')
        explosion.image = 'art/explosion2.png'
        explosion.layer = 'sprite'
        explosion.position.x = 400.0
        explosion.position.y = 100.0

        pug = PugSprite(gname='pug')
        pug.image = 'art/pug.png'
        pug.layer = 'two'
        pug.position.x = 400.0
        pug.position.y = 100.0

        REF___tjis = PugSprite(gname='1REF$# tjis')
        REF___tjis.color = (1.0, 0.0, 1.0, 1.0)
        REF___tjis.image = 'art/pug.png'
        REF___tjis.layer = 'two'
        REF___tjis.position.x = 501.0
        REF___tjis.position.y = 406.0

        # Pug auto-start
        self.start()
########################
# End "Three" autocode #
########################

