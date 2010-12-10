### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Face_Motion, Mouse_Follow
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (410.0, 310.0)

        pigsprite_instance_3 = PigSprite()
        pigsprite_instance_3.image = 'art\\pug.png'
        pigsprite_instance_3.layer = 'Background'
        pigsprite_instance_3.position = (420.0, 320.0)
        pigsprite_instance_3.components.add( Face_Motion() )
        pigsprite_instance_3.components.add( Mouse_Follow() )
### End MyScene autocode ###
