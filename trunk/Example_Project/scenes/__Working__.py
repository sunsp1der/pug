"""test.py"""

### import autocode ###
from objects.target import target
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Forward_Motion, Collision_Callback,\
    Key_Drive_Controls, Key_Spawn
### End import autocode ###

### test autocode ###
class test(PigScene):
    def on_enter(self):
        # Archetypes
        target_archetype = target(gname='target')
        target_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art/pig.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 503.0
        pigsprite_instance.position.y = 145.0
        pigsprite_instance.components.add( Forward_Motion(
                speed=-150) )
        pigsprite_instance.components.add( Collision_Callback(
                withGroup='arp') )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art/ufo2.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position.x = 394.0
        pigsprite_instance_2.position.y = 467.0
        pigsprite_instance_2.components.add( Key_Drive_Controls() )
        pigsprite_instance_2.components.add( Key_Spawn(
                key=1003,
                object='Growstar') )

        target_instance = target()
        target_instance.image = 'art/explosion2.png'
        target_instance.position.x = 407.0
        target_instance.position.y = 249.0

        target_instance_2 = target()
        target_instance_2.position.x = 427.0
        target_instance_2.position.y = 366.0
### End test autocode ###
