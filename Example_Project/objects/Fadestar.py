"""Fadestar.py"""

### import autocode ###
from pug.all_components import Fade
from pug.all_components import Self_Destruct
from pig.PigSprite import PigSprite
### End import autocode ###

### "Fadestar" autocode ###
class Fadestar(PigSprite):
    image = 'art/explosion2.png'
    layer = 'Stars'
    def on_create(self):
        self.position.x = 701.0
        self.position.y = 126.0
        self.components.add( Fade() )
        self.components.add( Self_Destruct() )
### End "Fadestar" autocode ###

