### import autocode ###
from objects.FlyAroundPlayerClass import FlyAroundPlayerClass
from objects.Target import Target
from pig.PigScene import PigScene
from pig.components.controls.Mouse_Face import Mouse_Face
from pug.all_components import On_Damaged_Sound, On_Damage_Sound
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Archetypes
        Target_archetype = Target(gname='Target')
        Target_archetype.archetype = True

        # Sprites
        flyaroundplayerclass_instance = FlyAroundPlayerClass()
        flyaroundplayerclass_instance.position = (255.0, 119.0)
        flyaroundplayerclass_instance.components.add( On_Damaged_Sound(
                sound='sound\\snap.wav') )
        flyaroundplayerclass_instance.components.remove_duplicate_of( Mouse_Face() )

        target_instance = Target()
        target_instance.position = (229.0, 321.0)
        target_instance.components.remove_duplicate_of( On_Damage_Sound(
                sound='sound\\snap.wav') )

        target_instance_2 = Target()
        target_instance_2.position = (231.0, 410.0)
### End MyScene autocode ###
