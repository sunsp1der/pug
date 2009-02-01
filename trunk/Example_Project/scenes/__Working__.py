"""__Working__.py"""

###################
# import autocode #
###################
from all_components import Face_Object
from objects.TestSprite import ShipSprite
from objects.jumpug import jumpug
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

######################
# "Spawny2" autocode #
######################
class Spawny2(PugScene):
    layers = ['Layer 1']
    def enter(self):
        # Archetypes
        jumpug_instance = jumpug(gname='jumpug')
        jumpug_instance.archetype = True

        # Sprites
        spawnero = PugSprite(gname='spawnero')
        spawnero.register = True
        spawnero.image = 'art/explosion2.png'
        spawnero.layer = 'Layer 1'
        spawnero.position.x = 434.0
        spawnero.position.y = 310.0
        spawnero.scale.x = 10.0
        spawnero.scale.y = 10.0

        jumpug_instance_2 = jumpug()
        jumpug_instance_2.components.add( Face_Object(
                target='spawnero',
                rotation_speed=20) )
        jumpug_instance_2.components.remove_duplicate_of( Face_Object(
                target='spawnero') )
        jumpug_instance_2.position.x = 300.0
        jumpug_instance_2.position.y = 188.0

        corny = ShipSprite(gname='corny')
        corny.register = True
        corny.layer = 'Layer 1'
        corny.position.x = 10.0
        corny.position.y = 10.0

        # Pug auto-start
        self.start()
##########################
# End "Spawny2" autocode #
##########################

