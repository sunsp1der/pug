### import autocode ###
from objects.DragonBreath import DragonBreath
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Textbox, Key_Animate_Direction, Key_Spawn
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
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (12.0, 544.0)
        pigsprite_instance_2.tint = (0, 0, 0)
        pigsprite_instance_2.components.add( Textbox(
                text='Keys: I, J, K, L, Space') )

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.layer = 'Sky'
        pigsprite_instance_3.position = (363.0, 263.0)
        pigsprite_instance_3.components.add( Key_Animate_Direction(
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
                rotate=True) )
        pigsprite_instance_3.components.add( Key_Spawn(
                spawn_object='DragonBreath',
                spawn_offset=(0.5, 0.050000000000000003)) )
### End Dragon autocode ###
