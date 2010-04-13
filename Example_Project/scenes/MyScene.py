### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art/pig.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 400.0
        pigsprite_instance.position.y = 300.0
### End MyScene autocode ###