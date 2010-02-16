"""test.py"""

### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Set_Motion, Collision_Callback,\
    Collision_Destroy
### End import autocode ###

### test autocode ###
class test(PigScene):
    layers = ['Background']
    def on_enter(self):
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

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art/pig.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position.x = 400.0
        pigsprite_instance_2.position.y = 300.0
        pigsprite_instance_2.components.add( Collision_Destroy(
                fromGroup='arp') )
### End test autocode ###
