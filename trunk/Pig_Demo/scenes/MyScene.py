### import autocode ###
from objects.FlyAroundPlayer import FlyAroundPlayer
from objects.SpawnWall import SpawnWall
from objects.Target import Target
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Utility_Keys, On_Start_Sound, Scene_On_Value,\
    Value_Tracker_Text, Textbox
### End import autocode ###

### MyScene autocode ###
class MyScene(Scene):
    layers = ['Background', 'walls']

    _Scene__node_num = 48
    def on_enter(self):
        self.components.add( Utility_Keys(
                info_F1='scenes/Fly_Around_Help.txt') )
        self.components.add( On_Start_Sound(
                sound='sound/beep.wav',
                loops=0) )
        self.components.add( Scene_On_Value(
                scene='MenuScreen',
                test_value=5) )

        # Archetypes
        Target_archetype = Target(gname='Target')
        Target_archetype.archetype = True

        FlyAroundPlayer_archetype = FlyAroundPlayer(gname='FlyAroundPlayer')
        FlyAroundPlayer_archetype.archetype = True

        SpawnWall_archetype = SpawnWall(gname='SpawnWall')
        SpawnWall_archetype.archetype = True

        # Sprites
        sprite_instance = Sprite()
        sprite_instance.layer = 'Background'
        sprite_instance.position = (678.0, 547.0)
        sprite_instance.components.add( Value_Tracker_Text() )

        sprite_instance_2 = Sprite()
        sprite_instance_2.layer = 'Background'
        sprite_instance_2.position = (678.0, 480.0)
        sprite_instance_2.components.add( Value_Tracker_Text(
                prefix='Health: ',
                value_name='health') )

        sprite_instance_3 = Sprite()
        sprite_instance_3.layer = 'Background'
        sprite_instance_3.position = (678.0, 513.0)
        sprite_instance_3.components.add( Value_Tracker_Text(
                prefix='Lives: ',
                value_name='lives') )

        sprite_instance_4 = Sprite()
        sprite_instance_4.layer = 'Background'
        sprite_instance_4.position = (20.0, 503.0)
        sprite_instance_4.components.add( Textbox(
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
### End MyScene autocode ###
