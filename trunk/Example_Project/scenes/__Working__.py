"""test.py"""

### import autocode ###
from objects.startarget import startarget
from objects.target import target
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Set_Motion, Collision_Callback,\
    Collision_Destroy
### End import autocode ###

### test autocode ###
class test(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Archetypes
        target_archetype = target(gname='target')
        target_archetype._archetype = True
        target_archetype.archetype = True

        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art/pig.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 391.0
        pigsprite_instance.position.y = 109.0
        pigsprite_instance.components.add( Set_Motion(
                velocity_y=150) )
        pigsprite_instance.components.add( Collision_Callback(
                withGroup='arp') )

        target_instance = target()
        target_instance.image = 'art/sprite.png'
        target_instance.position.x = 433.0
        target_instance.position.y = 388.0

        target_instance_2 = target()
        target_instance_2.image = 'art/ufo2.png'
        target_instance_2.position.x = 394.0
        target_instance_2.position.y = 467.0

        startarget_instance = startarget()
        startarget_instance.image = 'art/explosion2.png'
        startarget_instance.components.add( Collision_Destroy(
                fromGroup='arp') )
### End test autocode ###
