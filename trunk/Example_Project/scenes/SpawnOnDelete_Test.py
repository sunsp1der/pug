"""SpawnOnDelete_Test.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area
from objects.ExplodeParticle import ExplodeParticle
from objects.StarBomb import StarBomb
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#################################
# "SpawnOnDelete_Test" autocode #
#################################
class SpawnOnDelete_Test(PugScene):
    layers = ['Background']
    def on_enter(self):
        # Archetypes
        ExplodeParticle_archetype = ExplodeParticle(gname='ExplodeParticle')
        ExplodeParticle_archetype.archetype = True

        # Sprites
        starbomb_instance = StarBomb()

        pugsprite_instance = PugSprite()
        pugsprite_instance.image = 'art/pug.png'
        pugsprite_instance.layer = 'Background'
        pugsprite_instance.position.x = 401.0
        pugsprite_instance.position.y = 551.0
        pugsprite_instance.components.add( Spawn_Area(
                object='StarBomb',
                spawn_interval=3.0,
                spawn_location='center',
                spawn_offset=(0, -1)) )

#####################################
# End "SpawnOnDelete_Test" autocode #
#####################################

