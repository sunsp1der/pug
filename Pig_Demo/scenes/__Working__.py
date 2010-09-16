### import autocode ###
from objects.Bullet import Bullet
from objects.ExplodeParticle import ExplodeParticle
from objects.Launcher import Launcher
from objects.Target2 import Target2
from objects.cannon import cannon
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Spawner, Takes_Damage,\
    Value_Tracker_Text
### End import autocode ###

### Shooting_Gallery2 autocode ###
class Shooting_Gallery2(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( Utility_Keys(
                info_F1='scenes\\Shooting_Gallery_Help.txt') )

    def on_enter(self):
        # Archetypes
        Bullet_archetype = Bullet(gname='Bullet')
        Bullet_archetype.archetype = True

        ExplodeParticle_archetype = ExplodeParticle(gname='ExplodeParticle')
        ExplodeParticle_archetype.archetype = True

        Target2_archetype = Target2(gname='Target2')
        Target2_archetype.archetype = True

        # Sprites
        launcher_instance = Launcher()
        launcher_instance.position = (731.0, 142.0)

        launcher_instance_2 = Launcher()
        launcher_instance_2.position = (43.0, 175.0)
        launcher_instance_2.rotation = 90.0
        launcher_instance_2.components.add( Spawner(
                spawn_object='Target2',
                spawn_offset=(0, -1)) )
        launcher_instance_2.components.remove_duplicate_of( Spawner(
                spawn_object='Target',
                spawn_offset=(0, -1)) )

        cannon_instance = cannon()
        cannon_instance.position = (243.0, 179.0)
        cannon_instance.components.add( Takes_Damage() )
        cannon_instance.components.add( Takes_Damage() )

        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (672.0, 540.0)
        pigsprite_instance.components.add( Value_Tracker_Text() )
### End Shooting_Gallery2 autocode ###
