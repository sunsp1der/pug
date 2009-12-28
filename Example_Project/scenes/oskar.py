"""teste.py"""

### import autocode ###
from objects.YellowFacer import YellowFacer
from objects.PurpleFacer import PurpleFacer
from pig.PigScene import PigScene
### End import autocode ###

### "teste" autocode ###
class oskar(PigScene):
    def on_enter(self):
        # Sprites
        yellow1 = YellowFacer()
        yellow2 = PurpleFacer()
        yellow2.position = (50,50)
### End "teste" autocode ###

