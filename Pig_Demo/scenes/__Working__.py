### import autocode ###
from objects.Bullet import Bullet
from objects.Cannon import Cannon
from objects.ExplodeParticle import ExplodeParticle
from objects.Explosion import Explosion
from objects.Launcher import Launcher
from objects.Target import Target
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Joystick_Input, Joystick_Axis_To_Key,\
    Joystick_Button_To_Key, Value_Tracker_Text, Timer_Text, Textbox
### End import autocode ###

from objects.Grower import Grower

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        self.components.add( Joystick_Input(
                test_mode=True) )
        self.components.add( Joystick_Axis_To_Key() )
        self.components.add( Joystick_Button_To_Key() )

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

        cannon_instance = Cannon()

        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (666.0, 537.0)
        pigsprite_instance.components.add( Value_Tracker_Text() )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (667.0, 508.0)
        pigsprite_instance_2.components.add( Timer_Text() )

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.layer = 'Background'
        pigsprite_instance_3.position = (19.0, 530.0)
        pigsprite_instance_3.components.add( Textbox(
                text='Keys: J, L, Space') )
### End MyScene autocode ###

#
#    def on_start(self):
#        print "1"
#        for x in range(0,801,80):
#            for y in range(0,601,60):
#                Grower_instance = Grower(gname='Grower')
#                Grower_instance.position = (x, y)
#        print "2"
