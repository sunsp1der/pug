### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Animate_Grid
### End import autocode ###

from objects.Grower import Grower

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.components.add( Animate_Grid(
                file='art\\dragon.png',
                grid_width=75,
                grid_height=70) )
### End MyScene autocode ###

#
#    def on_start(self):
#        print "1"
#        for x in range(0,801,80):
#            for y in range(0,601,60):
#                Grower_instance = Grower(gname='Grower')
#                Grower_instance.position = (x, y)
#        print "2"
