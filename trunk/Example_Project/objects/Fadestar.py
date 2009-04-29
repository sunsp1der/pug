"""Fadestar.py"""

### import autocode ###
from all_components import Fade, Self_Destruct
from pug_opioid.PugSprite import PugSprite
### End import autocode ###

### "Fadestar" autocode ###
class Fadestar(PugSprite):
    image = 'art/explosion2.png'
    layer = 'Stars'
    def on_create(self):
        self.position.x = 701.0
        self.position.y = 126.0
        self.components.add( Fade() )
        self.components.add( Self_Destruct() )
### End "Fadestar" autocode ###

