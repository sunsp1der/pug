"""AimedSpawn.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area
from objects.PurpleFacer import PurpleFacer
from objects.UpFO import UpFO
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

#########################
# "AimedSpawn" autocode #
#########################
class AimedSpawn(PugScene):
    layers = ['Background']
    def enter(self):
        # Archetypes
        UpFO_archetype = UpFO(gname='UpFO')
        UpFO_archetype.archetype = True

        # Sprites
        purplefacer_instance = PurpleFacer()
        purplefacer_instance.components.add( Spawn_Area(
                object='UpFO',
                spawn_interval=0.29999999999999999,
                spawn_variance=0.0,
                spawn_location='center',
                spawn_offset=(0, -1)) )

        # Pug auto-start
        self.start()
#############################
# End "AimedSpawn" autocode #
#############################

