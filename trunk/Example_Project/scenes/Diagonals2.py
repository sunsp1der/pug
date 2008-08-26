###################
# import autocode #
###################
from pug_opioid.PugSprite import PugSprite
from Diagonals import Diagonals
from pug_opioid.components.physics.Set_Rotation_Speed import \
        Set_Rotation_Speed
#######################
# End import autocode #
#######################

#########################
# "Diagonals2" autocode #
#########################
class Diagonals2(Diagonals):    # Sprites etc.
    def enter(self):
        fred = PugSprite()
        fred.gname = 'fred'
        fred.components.add( Set_Rotation_Speed() )
        fred.image = 'art/sprite.png'
        fred.layer = 'bar'
        fred.position.x = 600.0
        fred.position.y = 450.0
        fred.scale.x = 3.0
        fred.scale.y = 1.0
        
        pugsprite_instance = PugSprite()
        pugsprite_instance.image = 'art/sprite.png'
        pugsprite_instance.layer = 'foo'
        pugsprite_instance.position.x = 400.0
        pugsprite_instance.position.y = 350.0

        pugsprite_instance_2 = PugSprite()
        pugsprite_instance_2.image = 'art/sprite.png'
        pugsprite_instance_2.layer = 'foo'
        pugsprite_instance_2.position.x = 200.0
        pugsprite_instance_2.position.y = 150.0

        pugsprite_instance_3 = PugSprite()
        pugsprite_instance_3.image = 'art/sprite.png'
        pugsprite_instance_3.layer = 'bar'
        pugsprite_instance_3.position.x = 250.0
        pugsprite_instance_3.position.y = 100.0

        pugsprite_instance_4 = PugSprite()
        pugsprite_instance_4.image = 'art/sprite.png'
        pugsprite_instance_4.layer = 'foo'
        pugsprite_instance_4.position.x = 250.0
        pugsprite_instance_4.position.y = 200.0

        pugsprite_instance_5 = PugSprite()
        pugsprite_instance_5.image = 'art/sprite.png'
        pugsprite_instance_5.layer = 'foo'
        pugsprite_instance_5.position.x = 100.0
        pugsprite_instance_5.position.y = 50.0

        pugsprite_instance_6 = PugSprite()
        pugsprite_instance_6.image = 'art/sprite.png'
        pugsprite_instance_6.layer = 'foo'
        pugsprite_instance_6.position.x = 300.0
        pugsprite_instance_6.position.y = 250.0

        pugsprite_instance_7 = PugSprite()
        pugsprite_instance_7.image = 'art/sprite.png'
        pugsprite_instance_7.layer = 'bar'
        pugsprite_instance_7.position.x = 650.0
        pugsprite_instance_7.position.y = 500.0

        pugsprite_instance_8 = PugSprite()
        pugsprite_instance_8.image = 'art/sprite.png'
        pugsprite_instance_8.layer = 'foo'
        pugsprite_instance_8.position.x = 450.0
        pugsprite_instance_8.position.y = 400.0

        pugsprite_instance_9 = PugSprite()
        pugsprite_instance_9.image = 'art/sprite.png'
        pugsprite_instance_9.layer = 'bar'
        pugsprite_instance_9.position.x = 350.0
        pugsprite_instance_9.position.y = 200.0

        pugsprite_instance_10 = PugSprite()
        pugsprite_instance_10.image = 'art/sprite.png'
        pugsprite_instance_10.layer = 'foo'
        pugsprite_instance_10.position.x = 350.0
        pugsprite_instance_10.position.y = 300.0

        pugsprite_instance_11 = PugSprite()
        pugsprite_instance_11.image = 'art/sprite.png'
        pugsprite_instance_11.layer = 'foo'
        pugsprite_instance_11.position.x = 500.0
        pugsprite_instance_11.position.y = 450.0

        pugsprite_instance_12 = PugSprite()
        pugsprite_instance_12.image = 'art/sprite.png'
        pugsprite_instance_12.layer = 'bar'
        pugsprite_instance_12.position.x = 400.0
        pugsprite_instance_12.position.y = 250.0

        pugsprite_instance_13 = PugSprite()
        pugsprite_instance_13.image = 'art/sprite.png'
        pugsprite_instance_13.layer = 'bar'
        pugsprite_instance_13.position.x = 450.0
        pugsprite_instance_13.position.y = 300.0

        pugsprite_instance_14 = PugSprite()
        pugsprite_instance_14.image = 'art/sprite.png'
        pugsprite_instance_14.layer = 'bar'
        pugsprite_instance_14.position.x = 200.0
        pugsprite_instance_14.position.y = 50.0

        pugsprite_instance_15 = PugSprite()
        pugsprite_instance_15.image = 'art/sprite.png'
        pugsprite_instance_15.layer = 'foo'
        pugsprite_instance_15.position.x = 550.0
        pugsprite_instance_15.position.y = 500.0

        pugsprite_instance_16 = PugSprite()
        pugsprite_instance_16.image = 'art/sprite.png'
        pugsprite_instance_16.layer = 'bar'
        pugsprite_instance_16.position.x = 550.0
        pugsprite_instance_16.position.y = 400.0

        pugsprite_instance_17 = PugSprite()
        pugsprite_instance_17.image = 'art/sprite.png'
        pugsprite_instance_17.layer = 'bar'
        pugsprite_instance_17.position.x = 300.0
        pugsprite_instance_17.position.y = 150.0

        pugsprite_instance_18 = PugSprite()
        pugsprite_instance_18.image = 'art/sprite.png'
        pugsprite_instance_18.layer = 'bar'
        pugsprite_instance_18.position.x = 500.0
        pugsprite_instance_18.position.y = 350.0

        pugsprite_instance_19 = PugSprite()
        pugsprite_instance_19.image = 'art/sprite.png'
        pugsprite_instance_19.layer = 'foo'
        pugsprite_instance_19.position.x = 150.0
        pugsprite_instance_19.position.y = 100.0

        self.start()
#############################
# End "Diagonals2" autocode #
#############################
