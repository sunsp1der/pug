### import autocode ###
from objects.FlyAroundPlayer import FlyAroundPlayer
from objects.SpawnWall import SpawnWall
from objects.Target import Target
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, On_Start_Sound,\
    Value_Tracker_Text, Textbox
### End import autocode ###

### Fly_Around autocode ###
class Fly_Around(PigScene):
    layers = ['Background', 'walls']

    def on_enter(self):
        self.components.add( Utility_Keys(
                info_F1='scenes\\Fly_Around_Help.txt') )
        self.components.add( On_Start_Sound(
                sound='sound\\beep.wav',
                loops=0) )

        # Archetypes
        Target_archetype = Target(gname='Target')
        Target_archetype.archetype = True

        FlyAroundPlayer_archetype = FlyAroundPlayer(gname='FlyAroundPlayer')
        FlyAroundPlayer_archetype.archetype = True

        SpawnWall_archetype = SpawnWall(gname='SpawnWall')
        SpawnWall_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (678.0, 547.0)
        pigsprite_instance.components.add( Value_Tracker_Text() )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (678.0, 480.0)
        pigsprite_instance_2.components.add( Value_Tracker_Text(
                prefix='Health: ',
                value_name='health') )

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.layer = 'Background'
        pigsprite_instance_3.position = (678.0, 513.0)
        pigsprite_instance_3.components.add( Value_Tracker_Text(
                prefix='Lives: ',
                value_name='lives') )

        pigsprite_instance_4 = PigSprite()
        pigsprite_instance_4.layer = 'Background'
        pigsprite_instance_4.position = (20.0, 503.0)
        pigsprite_instance_4.components.add( Textbox(
                text='Keys: W, A, S, D Mouse: Aim, Fire',
                max_width=220) )

        spawnwall_instance = SpawnWall()
        spawnwall_instance.position = (400.0, 595.0)
        spawnwall_instance.scale = (400.0, 5.0)

        spawnwall_instance_2 = SpawnWall()
        spawnwall_instance_2.position = (400.0, 5.0)
        spawnwall_instance_2.scale = (400.0, 5.0)
        spawnwall_instance_2.rotation = 180.0

        spawnwall_instance_3 = SpawnWall()
        spawnwall_instance_3.position = (400.0, 5.0)
        spawnwall_instance_3.scale = (400.0, 5.0)
        spawnwall_instance_3.rotation = 180.0

        spawnwall_instance_4 = SpawnWall()
        spawnwall_instance_4.position = (5.0, 300.0)
        spawnwall_instance_4.scale = (300.0, 5.0)
        spawnwall_instance_4.rotation = 90.0

        spawnwall_instance_5 = SpawnWall()
        spawnwall_instance_5.position = (795.0, 300.0)
        spawnwall_instance_5.scale = (300.0, 5.0)
        spawnwall_instance_5.rotation = 270.0
### End Fly_Around autocode ###
