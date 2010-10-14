### import autocode ###
from objects.DragonBreath import DragonBreath
from objects.RedDragon import RedDragon
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Textbox, Key_Spawn
### End import autocode ###

### Dragon autocode ###
class Dragon(PigScene):
    layers = ['Background', 'Sky']

    def on_enter(self):
        # Archetypes
        DragonBreath_archetype = DragonBreath(gname='DragonBreath')
        DragonBreath_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\cloudscape 1b.jpg'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.scale = (1.2999999523162842, 1.5)

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.layer = 'Sky'
        pigsprite_instance_2.position = (12.0, 544.0)
        pigsprite_instance_2.tint = (0, 0, 0)
        pigsprite_instance_2.components.add( Textbox(
                text='Keys: I, J, K, L, Space') )

        RedDragon_instance = RedDragon(gname='RedDragon')
        RedDragon_instance.components.add( Key_Spawn(
                spawn_object='DragonBreath',
                spawn_offset=(0.5, 0.050000000000000003)) )
        RedDragon_instance.components.remove_duplicate_of( Key_Spawn(
                spawn_object='DragonBreath',
                spawn_offset=(0.5, 0.050000000000000003)) )
### End Dragon autocode ###
