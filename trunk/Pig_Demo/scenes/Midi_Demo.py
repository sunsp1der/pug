### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Midi_Input, Spawn_On_Midi,\
    Midi_Rainbow
### End import autocode ###

### Midi_Demo autocode ###
class Midi_Demo(PigScene):
    def on_enter(self):
        self.components.add( Utility_Keys() )
        self.components.add( Midi_Input() )

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (70.0, 125.0)
        pigsprite_instance.rotation = 90.0
        pigsprite_instance.components.add( Spawn_On_Midi(
                spawn_object='Target',
                spawn_interval=0.4,
                spawn_interval_variance=0.0,
                obs_per_spawn=2,
                obs_per_spawn_variance=1) )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (69.0, 392.0)
        pigsprite_instance_2.rotation = 90.0
        pigsprite_instance_2.components.add( Midi_Rainbow(
                spawn_object='Target',
                spawn_interval=0.4,
                spawn_interval_variance=0.0,
                obs_per_spawn=2,
                obs_per_spawn_variance=1) )
### End Midi_Demo autocode ###
