### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Set_Motion, Grow_Shrink, Life_Zone
### End import autocode ###

### UpFO autocode ###
class UpFO(PigSprite):
    image = 'art/red nose reindeer.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 380.0
        self.position.y = 208.0
        self.components.add( Set_Motion(
                velocity_y=-500) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.5) )
        self.components.add( Life_Zone() )
### End UpFO autocode ###
