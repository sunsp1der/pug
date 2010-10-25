### import autocode ###
from objects.Flamebit import Flamebit
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Midi_Input, Spawn_On_Midi,\
    Spawn_Flower
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        self.components.add( Utility_Keys() )
        self.components.add( Midi_Input() )

        # Archetypes
        Flamebit_archetype = Flamebit(gname='Flamebit')
        Flamebit_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (408.0, 336.0)
        pigsprite_instance.components.add( Spawn_On_Midi(
                spawn_object='Flamebit',
                spawn_interval=1.0,
                spawn_interval_variance=0.0,
                spawn_offset=(0.5, 0.0)) )
        pigsprite_instance.components.add( Spawn_Flower(
                h_symmetry=True,
                v_symmetry=True) )
### End MyScene autocode ###
