"""SpawnEffects_Test.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area
from objects.Fadestar import Fadestar
from objects.YellowPug import YellowPug
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

################################
# "SpawnEffects_Test" autocode #
################################
class SpawnEffects_Test(PugScene):
    layers = ['Background']
    def on_enter(self):
        # Archetypes
        Fadestar_archetype = Fadestar(gname='Fadestar')
        Fadestar_archetype.archetype = True

        # Sprites
        yellowpug_instance = YellowPug()
        yellowpug_instance.position.x = 397.0
        yellowpug_instance.position.y = 313.0
        yellowpug_instance.scale.x = 5.0
        yellowpug_instance.scale.y = 5.0
        yellowpug_instance.components.add( Spawn_Area(
                object='Fadestar',
                spawn_interval=0.5,
                spawn_variance=0.29999999999999999,
                match_velocity=True) )

        yellowpug_instance.components.add( Spawn_Area(
                object='Growstar',
                spawn_interval=0.5,
                spawn_variance=0.29999999999999999,
                match_velocity=True) )

####################################
# End "SpawnEffects_Test" autocode #
####################################

