### import autocode ###
from pig.PigScene import PigScene
### End import autocode ###

from objects.Grower import Grower

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        pass
### End MyScene autocode ###

    def on_start(self):
        for x in range(0,801,80):
            for y in range(0,601,60):
                Grower_instance = Grower(gname='Grower')
                Grower_instance.position = (x, y)
