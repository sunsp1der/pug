###################
# import autocode #
###################
from all_components import Set_Motion
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
#######################
# End import autocode #
#######################

######################
# "Jumpers" autocode #
######################
class Jumpers(PugScene):
    layers = ['new_layer']
    def enter(self):
        # Sprites etc.
        jumpug = PugSprite(gname='jumpug')
        jumpug.components.add( Set_Motion(
                velocity_y=-400, 
                acceleration_y=200, 
                rotation_speed=1, ) )
        jumpug.image = 'art/pug.png'
        jumpug.layer = 'new_layer'
        jumpug.position.x = 155.0
        jumpug.position.y = 513.0

        jumpug_2 = PugSprite(gname='jumpug')
        jumpug_2.alpha = 0.30000001192092896
        jumpug_2.color = (0.0, 1.0, 0.5, 0.30000001192092896)
        jumpug_2.components.add( Set_Motion(
                velocity_y=-400, 
                acceleration_y=200, 
                rotation_speed=1, ) )
        jumpug_2.image = 'art/pug.png'
        jumpug_2.layer = 'new_layer'
        jumpug_2.position.x = 276.0
        jumpug_2.position.y = 406.0

        jumpug_3 = PugSprite(gname='jumpug')
        jumpug_3.components.add( Set_Motion(
                velocity_y=-400, 
                acceleration_y=200, 
                rotation_speed=1, ) )
        jumpug_3.image = 'art/explosion2.png'
        jumpug_3.layer = 'new_layer'
        jumpug_3.position.x = 550.0
        jumpug_3.position.y = 473.0

        jumpug_4 = PugSprite(gname='jumpug')
        jumpug_4.components.add( Set_Motion(
                velocity_y=-400, 
                acceleration_y=200, 
                rotation_speed=1, ) )
        jumpug_4.image = 'art/pug.png'
        jumpug_4.layer = 'new_layer'
        jumpug_4.position.x = 212.0
        jumpug_4.position.y = 267.0

        red = PugSprite(gname='red')
        red.color = (1.0, 0.0, 0.0, 1.0)
        red.components.add( Set_Motion(
                velocity_y=-300, 
                acceleration_y=200, 
                rotation_speed=30, ) )
        red.image = 'art/pug.png'
        red.layer = 'new_layer'
        red.position.x = 268.0
        red.position.y = 406.0

        # Pug auto-start
        self.start()
##########################
# End "Jumpers" autocode #
##########################
