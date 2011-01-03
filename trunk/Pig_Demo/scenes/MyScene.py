### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 298.5)
        pigsprite_instance.scale = (1.0, 0.9625)
        pigsprite_instance.rotation = 45.0
### End MyScene autocode ###
