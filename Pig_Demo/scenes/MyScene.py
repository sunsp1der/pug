### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Mouse_Face
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.scale = (10.0, 10.0)
        pigsprite_instance.components.add( Mouse_Face(
                rotation_speed=30) )
### End MyScene autocode ###
