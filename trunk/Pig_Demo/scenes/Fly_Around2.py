### import autocode ###
from objects.FlyAroundPlayerClass import FlyAroundPlayerClass
from objects.SpawnWall import SpawnWall
from objects.Target import Target
from pig.PigScene import PigScene
from pug.all_components import Utility_Keys, On_Start_Sound
### End import autocode ###

### Fly_Around2 autocode ###
class Fly_Around2(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( Utility_Keys(
                info_F1='scenes\\Fly_Around_Help.txt') )
        self.components.add( On_Start_Sound(
                sound='sound\\snap.wav',
                loops=0) )

    layers = ['Background', 'walls']
    def on_enter(self):
        # Archetypes
        Target_archetype = Target(gname='Target')
        Target_archetype.archetype = True

        SpawnWall_archetype = SpawnWall(gname='SpawnWall')
        SpawnWall_archetype.archetype = True

        # Sprites
        FlyAroundPlayer = FlyAroundPlayerClass(gname='FlyAroundPlayer')

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
### End Fly_Around2 autocode ###
