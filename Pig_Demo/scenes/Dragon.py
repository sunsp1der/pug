### import autocode ###
from objects.DragonBreath import DragonBreath
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Key_Animate_Direction, Key_Spawn
### End import autocode ###

### Dragon autocode ###
class Dragon(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( Utility_Keys() )

    def on_enter(self):
        # Archetypes
        DragonBreath_archetype = DragonBreath(gname='DragonBreath')
        DragonBreath_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (363.0, 263.0)
        pigsprite_instance.components.add( Key_Animate_Direction(
                file='art\\dragon.png',
                grid_width=75,
                grid_height=70,
                up_frames=(60, 70),
                upright_frames=(70, 80),
                right_frames=(0, 10),
                downright_frames=(10, 20),
                down_frames=(20, 30),
                downleft_frames=(30, 40),
                left_frames=(40, 50),
                upleft_frames=(50, 60),
                rotate=True,
                up_key=105,
                down_key=107,
                left_key=106,
                right_key=108) )
        pigsprite_instance.components.add( Key_Spawn(
                spawn_object='DragonBreath',
                spawn_offset=(0.5, 0.05)) )
### End Dragon autocode ###
