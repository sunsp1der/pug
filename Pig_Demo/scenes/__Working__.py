### import autocode ###
from components.Mouse_Face import Mouse_Face as Mouse_Face_2
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pig.components.controls.Mouse_Face import Mouse_Face as Mouse_Face_3
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
        pigsprite_instance.components.add( Mouse_Face() )
        pigsprite_instance.components.add( Mouse_Face_2() )
        pigsprite_instance.components.add( Mouse_Face_3() )
### End MyScene autocode ###
