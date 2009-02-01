"""Spawny.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area
from objects.TestSprite import ShipSprite
from objects.jumpug import jumpug
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#####################
# "Spawny" autocode #
#####################
class Spawny(PugScene):
    layers = ['Layer 1']
    def enter(self):
        # Archetypes
        jumpug_instance = jumpug(gname='jumpug')
        jumpug_instance.archetype = True

        # Sprites
        spawnero = PugSprite(gname='spawnero')
        spawnero.components.add( Spawn_Area(
                object=u'jumpug') )
        spawnero.image = 'art/explosion2.png'
        spawnero.layer = 'Layer 1'
        spawnero.position.x = 434.0
        spawnero.position.y = 310.0
        spawnero.scale.x = 10.0
        spawnero.scale.y = 10.0

        jumpug_instance_2 = jumpug()
        jumpug_instance_2.position.x = 261.0
        jumpug_instance_2.position.y = 197.0

        jumpug_instance_3 = jumpug()
        jumpug_instance_3.position.x = 543.0
        jumpug_instance_3.position.y = 410.0

        corny = ShipSprite(gname='corny')
        corny.layer = 'Layer 1'
        corny.position.x = 10.0
        corny.position.y = 10.0

        # Pug auto-start
        self.start()
#########################
# End "Spawny" autocode #
#########################

