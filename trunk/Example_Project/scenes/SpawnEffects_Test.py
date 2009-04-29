"""SpawnEffects_Test.py"""

### import autocode ###
from all_components import Grow_Shrink, Self_Destruct, Spawn_Area
from objects.Fadestar import Fadestar
from objects.Growstar import GrowStar
from objects.YellowPug import YellowPug
from pug_opioid.PugScene import PugScene
### End import autocode ###

### "SpawnEffects_Test" autocode ###
class SpawnEffects_Test(PugScene):
    layers = ['Background', 'Stars']
    def on_enter(self):
        # Archetypes
        Fadestar_archetype = Fadestar(gname='Fadestar')
        Fadestar_archetype.archetype = True

        GrowStar_archetype = GrowStar(gname='GrowStar')
        GrowStar_archetype.archetype = True
        GrowStar_archetype.components.add( Grow_Shrink() )
        GrowStar_archetype.components.add( Self_Destruct() )

        # Sprites
        yellowpug_instance = YellowPug()
        yellowpug_instance.position.x = 397.0
        yellowpug_instance.position.y = 313.0
        yellowpug_instance.scale.x = 5.0
        yellowpug_instance.scale.y = 5.0
        yellowpug_instance.components.add( Spawn_Area(
                object='Fadestar',
                spawn_interval=0.5,
                spawn_variance=0.29999999999999999) )
        yellowpug_instance.components.add( Spawn_Area(
                object='Growstar',
                spawn_interval=0.5,
                spawn_variance=0.29999999999999999) )
### End "SpawnEffects_Test" autocode ###

