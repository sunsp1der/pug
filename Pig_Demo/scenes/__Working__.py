### import autocode ###
from objects.Bullet import Bullet
from objects.ExplodeParticle import ExplodeParticle
from objects.Launcher import Launcher
from objects.Target import Target
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Key_Drive_Controls, Key_Spawn,\
    Value_Tracker_Text
### End import autocode ###

### Shooting_Gallery autocode ###
class Shooting_Gallery(PigScene):
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

        Target_archetype = Target(gname='Target')
        Target_archetype.archetype = True

        # Sprites
        launcher_instance = Launcher()

        launcher_instance_2 = Launcher()
        launcher_instance_2.position = (43.0, 175.0)
        launcher_instance_2.rotation = 90.0

        cannon = PigSprite(gname='cannon')
        cannon.image = 'art\\pug.png'
        cannon.layer = 'Background'
        cannon.position = (400.0, 514.0)
        cannon.opacity = 0.5
        cannon.components.add( Key_Drive_Controls(
                forward_key=None,
                backward_key=None) )
        cannon.components.add( Key_Spawn(
                spawn_object='Bullet',
                sound='sound\\snap.wav',
                spawn_offset=(0, -1),
                max_spawns_in_scene=1) )

        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (702.0, 542.0)
        pigsprite_instance.components.add( Value_Tracker_Text() )
### End Shooting_Gallery autocode ###
