###################
# import autocode #
###################
from all_components import Set_Motion, Follow_Mouse, Set_Motion, \
        Face_Object
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

########################
# "Diagonals" autocode #
########################
class Diagonals(PugScene):
    layers = ['bar']
    def enter(self):
        # Sprites etc.
        pugsprite_instance = PugSprite()
        pugsprite_instance.components.add( Set_Motion(
                rotation_speed=80, ) )
        pugsprite_instance.image = 'art/sprite.png'
        pugsprite_instance.layer = 'bar'
        pugsprite_instance.position.x = 600.0
        pugsprite_instance.position.y = 200.0
        pugsprite_instance.scale.x = 3.0
        pugsprite_instance.scale.y = 1.0

        pugsprite_instance_2 = PugSprite()
        pugsprite_instance_2.image = 'art/sprite.png'
        pugsprite_instance_2.layer = 'bar'
        pugsprite_instance_2.position.x = 550.0
        pugsprite_instance_2.position.y = 400.0

        playa = PugSprite(gname='playa')
        playa.components.add( Follow_Mouse() )
        playa.components.add( Set_Motion(
                rotation_speed=25, ) )
        playa.image = 'art/sprite.png'
        playa.layer = 'bar'
        playa.position.x = 430.0
        playa.position.y = 419.0

        pugsprite_instance_3 = PugSprite()
        pugsprite_instance_3.image = 'art/sprite.png'
        pugsprite_instance_3.layer = 'bar'
        pugsprite_instance_3.position.x = 500.0
        pugsprite_instance_3.position.y = 350.0

        pugsprite_instance_4 = PugSprite()
        pugsprite_instance_4.image = 'art/sprite.png'
        pugsprite_instance_4.layer = 'bar'
        pugsprite_instance_4.position.x = 250.0
        pugsprite_instance_4.position.y = 100.0

        pugsprite_instance_5 = PugSprite()
        pugsprite_instance_5.components.add( Face_Object(
                target='playa', ) )
        pugsprite_instance_5.image = 'art/sprite.png'
        pugsprite_instance_5.layer = 'bar'
        pugsprite_instance_5.position.x = 350.0
        pugsprite_instance_5.position.y = 200.0

        pugsprite_instance_6 = PugSprite()
        pugsprite_instance_6.image = 'art/sprite.png'
        pugsprite_instance_6.layer = 'bar'
        pugsprite_instance_6.position.x = 450.0
        pugsprite_instance_6.position.y = 300.0

        pugsprite_instance_7 = PugSprite()
        pugsprite_instance_7.image = 'art/sprite.png'
        pugsprite_instance_7.layer = 'bar'
        pugsprite_instance_7.position.x = 400.0
        pugsprite_instance_7.position.y = 250.0

        pugsprite_instance_8 = PugSprite()
        pugsprite_instance_8.image = 'art/sprite.png'
        pugsprite_instance_8.layer = 'bar'
        pugsprite_instance_8.position.x = 650.0
        pugsprite_instance_8.position.y = 500.0

        pugsprite_instance_9 = PugSprite()
        pugsprite_instance_9.components.add( Set_Motion(
                rotation_speed=500, ) )
        pugsprite_instance_9.image = 'art/explosion2.png'
        pugsprite_instance_9.layer = 'bar'
        pugsprite_instance_9.position.x = 125.0
        pugsprite_instance_9.position.y = 374.0

        playa_2 = PugSprite(gname='playa')
        playa_2.components.add( Follow_Mouse() )
        playa_2.components.add( Set_Motion(
                rotation_speed=25, ) )
        playa_2.image = 'art/pug.png'
        playa_2.layer = 'bar'
        playa_2.position.x = 430.0
        playa_2.position.y = 419.0
        playa_2.color = (0,0,1,1)

        # Pug auto-start
        self.start()
############################
# End "Diagonals" autocode #
############################
