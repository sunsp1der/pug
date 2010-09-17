### import autocode ###
from objects.Bullet import Bullet
from objects.ExplodeParticle import ExplodeParticle
from objects.Explosion import Explosion
from objects.Launcher import Launcher
from objects.Target import Target
from objects.cannon import cannon
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Value_Tracker_Text, Timer_Text
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

        Explosion_archetype = Explosion(gname='Explosion')
        Explosion_archetype.archetype = True

        # Sprites
        launcher_instance = Launcher()
        launcher_instance.position = (731.0, 142.0)

        launcher_instance_2 = Launcher()
        launcher_instance_2.position = (43.0, 175.0)
        launcher_instance_2.rotation = 90.0

        cannon_instance = cannon()

        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (666.0, 537.0)
        pigsprite_instance.components.add( Value_Tracker_Text() )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (667.0, 508.0)
        pigsprite_instance_2.components.add( Timer_Text() )
### End Shooting_Gallery autocode ###
