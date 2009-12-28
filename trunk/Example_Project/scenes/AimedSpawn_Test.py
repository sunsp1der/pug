#1

### import autocode ###
from objects.PurpleFacer import PurpleFacer
from objects.UpFO import UpFO
from pug.all_components import Spawn_Area
from pig.PigScene import PigScene
### End import autocode ###

#2

### AimedSpawn_Test autocode ###
class AimedSpawn_Test(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Archetypes
        UpFO_archetype = UpFO(gname='UpFO')
        UpFO_archetype.archetype = True

        # Sprites
        purplefacer_instance = PurpleFacer()
        purplefacer_instance.image = 'art/cannon.png'
        purplefacer_instance.position.x = 432.0
        purplefacer_instance.position.y = 459.0
        purplefacer_instance.components.add( Spawn_Area(
                object='UpFO',
                spawn_interval=0.3,
                spawn_variance=0.0,
                spawn_location='right',
                spawn_offset=(1, 0)) )
        purplefacer_instance.components.add( Spawn_Area(
                object='UpFO',
                spawn_interval=0.3,
                spawn_variance=0.0,
                spawn_location='left',
                spawn_offset=(1, 0)) )
### End AimedSpawn_Test autocode ###

        purplefacer_instance.position.x = 0
