"""__Working__.py"""

###################
# import autocode #
###################
from all_components import Spawn_Area, Forward_Motion
from objects.PurpleFacer import PurpleFacer
from objects.UpFO import UpFO
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

##############################
# "AimedSpawn_Test" autocode #
##############################
class AimedSpawn_Test(PugScene):
    layers = ['Background']
    def on_enter(self):
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
                spawn_offset=(1, 0)) )
        purplefacer_instance.components.add( Forward_Motion(
                velocity=50) )

##################################
# End "AimedSpawn_Test" autocode #
##################################

