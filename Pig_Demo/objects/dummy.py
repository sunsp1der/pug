### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Self_Destruct, Textbox, Set_Motion
### End import autocode ###

### dummy autocode ###
class dummy(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (626.0, 420.0)
        self.components.add( Self_Destruct() )
        self.components.add( Textbox() )
        self.components.add( Set_Motion(
                velocity_y=-200) )
### End dummy autocode ###
