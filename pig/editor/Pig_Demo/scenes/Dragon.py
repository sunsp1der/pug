### import autocode ###
from objects.DragonBreath import DragonBreath
from objects.RedDragon import RedDragon
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Utility_Keys, Textbox
### End import autocode ###

### Dragon autocode ###
class Dragon(Scene):
    layers = ['Background', 'Sky']

    def on_enter(self):
        self.components.add( Utility_Keys() )

        # Archetypes
        DragonBreath_archetype = DragonBreath(gname='DragonBreath')
        DragonBreath_archetype.archetype = True

        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/cloudscape 1b.jpg'
        sprite_instance.layer = 'Background'
        sprite_instance.position = (400.0, 300.0)
        sprite_instance.scale = (1.3, 1.5)

        sprite_instance_2 = Sprite()
        sprite_instance_2.layer = 'Sky'
        sprite_instance_2.position = (12.0, 544.0)
        sprite_instance_2.tint = (0, 0, 0)
        sprite_instance_2.components.add( Textbox(
                text='Keys: I, J, K, L, Space') )

        RedDragon_instance = RedDragon(gname='RedDragon')
### End Dragon autocode ###
