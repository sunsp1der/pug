### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Grow_Shrink, Set_Motion, Life_Zone
### End import autocode ###

### DragonBreath autocode ###
class DragonBreath(PigSprite):
    image = 'art\\explosion\\explosion09.png'
    layer = 'Sky'
    def on_create(self):
        self.position = (536.0, 341.0)
        self.scale = (0.5, 0.5)
        self.components.add( Grow_Shrink(
                grow_in_secs=0.3) )
        self.components.add( Set_Motion(
                velocity_y=-500,
                rotation_speed=100) )
        self.components.add( Life_Zone() )
### End DragonBreath autocode ###
