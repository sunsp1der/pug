###################
# import autocode #
###################
from all_components import Follow_Mouse, Set_Rotation_Speed, Set_Motion, \
        Face_Object
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

#########################
# "Diagonals3" autocode #
#########################
class Diagonals3(PugScene):
    gname = 'Diagonals3'
    layers = ['foo', 'bar']
    def enter(self):
        # Sprites etc.
        pugsprite_instance = PugSprite()
        pugsprite_instance.image = 'art/sprite.png'
        pugsprite_instance.layer = 'bar'
        pugsprite_instance.position.x = 607.0
        pugsprite_instance.position.y = 258.0

        pugsprite_instance_2 = PugSprite()
        pugsprite_instance_2.image = 'art/sprite.png'
        pugsprite_instance_2.layer = 'bar'
        pugsprite_instance_2.position.x = 650.0
        pugsprite_instance_2.position.y = 500.0

        pugsprite_instance_3 = PugSprite()
        pugsprite_instance_3.image = 'art/sprite.png'
        pugsprite_instance_3.layer = 'bar'
        pugsprite_instance_3.position.x = 400.0
        pugsprite_instance_3.position.y = 250.0

        pugsprite_instance_4 = PugSprite()
        pugsprite_instance_4.image = 'art/sprite.png'
        pugsprite_instance_4.layer = 'bar'
        pugsprite_instance_4.position.x = 450.0
        pugsprite_instance_4.position.y = 300.0

        pugsprite_instance_5 = PugSprite()
        pugsprite_instance_5.image = 'art/sprite.png'
        pugsprite_instance_5.layer = 'bar'
        pugsprite_instance_5.position.x = 350.0
        pugsprite_instance_5.position.y = 200.0

        pugsprite_instance_6 = PugSprite()
        pugsprite_instance_6.image = 'art/sprite.png'
        pugsprite_instance_6.layer = 'bar'
        pugsprite_instance_6.position.x = 250.0
        pugsprite_instance_6.position.y = 100.0

        pugsprite_instance_7 = PugSprite()
        pugsprite_instance_7.image = 'art/sprite.png'
        pugsprite_instance_7.layer = 'bar'
        pugsprite_instance_7.position.x = 500.0
        pugsprite_instance_7.position.y = 350.0

        playa = PugSprite(gname='playa')
        playa.components.add( Follow_Mouse(
                face_movement=True, ) )
        playa.image = 'art/pug.png'
        playa.layer = 'bar'
        playa.position.x = 361.0
        playa.position.y = 317.0

        pugsprite_instance_8 = PugSprite()
        pugsprite_instance_8.image = 'art/sprite.png'
        pugsprite_instance_8.layer = 'bar'
        pugsprite_instance_8.position.x = 550.0
        pugsprite_instance_8.position.y = 400.0

        pugsprite_instance_9 = PugSprite()
        pugsprite_instance_9.components.add( Set_Rotation_Speed(
                rotation_speed=80, ) )
        pugsprite_instance_9.image = 'art/sprite.png'
        pugsprite_instance_9.layer = 'bar'
        pugsprite_instance_9.position.x = 600.0
        pugsprite_instance_9.position.y = 200.0
        pugsprite_instance_9.scale.x = 3.0
        pugsprite_instance_9.scale.y = 1.0

        pugsprite_instance_10 = PugSprite()
        pugsprite_instance_10.image = 'art/sprite.png'
        pugsprite_instance_10.layer = 'foo'
        pugsprite_instance_10.position.x = 200.0
        pugsprite_instance_10.position.y = 150.0

        pugsprite_instance_11 = PugSprite()
        pugsprite_instance_11.friction = 0.89999997615814209
        pugsprite_instance_11.components.add( Set_Rotation_Speed() )
        pugsprite_instance_11.components.add( Set_Motion(
                velocity_x=100, 
                velocity_y=100, 
                friction=0.90000000000000002, ) )
        pugsprite_instance_11.image = 'art/sprite.png'
        pugsprite_instance_11.layer = 'foo'
        pugsprite_instance_11.position.x = 318.92327880859375
        pugsprite_instance_11.position.y = 268.92327880859375
        pugsprite_instance_11.velocity.x = 5.6051938572992683e-45
        pugsprite_instance_11.velocity.y = 5.6051938572992683e-45

        pugsprite_instance_12 = PugSprite()
        pugsprite_instance_12.image = 'art/sprite.png'
        pugsprite_instance_12.layer = 'foo'
        pugsprite_instance_12.position.x = 250.0
        pugsprite_instance_12.position.y = 200.0

        pugsprite_instance_13 = PugSprite()
        pugsprite_instance_13.image = 'art/sprite.png'
        pugsprite_instance_13.layer = 'foo'
        pugsprite_instance_13.position.x = 150.0
        pugsprite_instance_13.position.y = 100.0

        pugsprite_instance_14 = PugSprite()
        pugsprite_instance_14.image = 'art/sprite.png'
        pugsprite_instance_14.layer = 'foo'
        pugsprite_instance_14.position.x = 500.0
        pugsprite_instance_14.position.y = 450.0

        pugsprite_instance_15 = PugSprite()
        pugsprite_instance_15.image = 'art/sprite.png'
        pugsprite_instance_15.layer = 'foo'
        pugsprite_instance_15.position.x = 100.0
        pugsprite_instance_15.position.y = 50.0

        pugsprite_instance_16 = PugSprite()
        pugsprite_instance_16.image = 'art/sprite.png'
        pugsprite_instance_16.layer = 'foo'
        pugsprite_instance_16.position.x = 389.0
        pugsprite_instance_16.position.y = 292.0

        pugsprite_instance_17 = PugSprite()
        pugsprite_instance_17.components.add( Face_Object(
                target='playa', 
                rotation_speed=250, 
                offset=-90, ) )
        pugsprite_instance_17.image = 'art/sprite.png'
        pugsprite_instance_17.layer = 'foo'
        pugsprite_instance_17.position.x = 117.0
        pugsprite_instance_17.position.y = 332.0

        pugsprite_instance_18 = PugSprite()
        pugsprite_instance_18.image = 'art/sprite.png'
        pugsprite_instance_18.layer = 'foo'
        pugsprite_instance_18.position.x = 550.0
        pugsprite_instance_18.position.y = 500.0

        there = PugSprite(gname='hi there')
        there.image = 'art/sprite.png'
        there.layer = 'foo'
        there.position.x = 413.0
        there.position.y = 291.0

        # Pug auto-start
        self.start()
#############################
# End "Diagonals3" autocode #
#############################
