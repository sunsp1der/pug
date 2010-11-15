### import autocode ###
from pig.PigSprite import PigSprite
### End import autocode ###

from pig.util import get_mouse_position, Vector
from pig.actions import RealTickFunc

### Grower autocode ###
class Grower(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (400.0, 300.0)
### End Grower autocode ###

    def on_scene_start(self, scene):
        self.threshold = 100 * 100
        self.scale_multiplier = 3
        self.original_scale = Vector(self.scale.x, self.scale.y)
        RealTickFunc(self.check_mouse).do()

    def check_mouse(self):
        position = get_mouse_position()
        dist = pow(self.position[0] - position[0],2) + \
                pow(self.position[1] - position[1],2)
        change = self.threshold - dist
        if change > 0:
            grow_amount = (change/self.threshold) * self.scale_multiplier
            self.scale = self.original_scale * (1+grow_amount)
#            rotate_amount = (change/self.threshold) * 360
#            self.rotation = rotate_amount
#            alpha_amount = (change/self.threshold) 
#            self.alpha = alpha_amount
        else:
#            self.alpha = 0
#            self.rotation = 0
            self.scale = self.original_scale
        
