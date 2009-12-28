"""Growstar.py"""

### import autocode ###
from pug.all_components import Grow_Shrink, Self_Destruct
from pig.PigSprite import PigSprite
### End import autocode ###

### "Growstar" autocode ###
class Growstar(PigSprite):
    image = 'art/explosion2.png'
    layer = 'Stars'
    def on_create(self):
        self.position.x = 317.0
        self.position.y = 85.0
        self.components.add( Grow_Shrink() )
        self.components.add( Self_Destruct() )
### End "Growstar" autocode ###

