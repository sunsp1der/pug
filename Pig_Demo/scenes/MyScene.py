### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\block.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.scale = (10.0, 10.0)
### End MyScene autocode ###
