### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Textbox
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (182.0, 83.0)
        pigsprite_instance.scale = (7.75, 9.147)
        pigsprite_instance.components.add( Textbox(
                text='ore') )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (618.0, 346.25)
        pigsprite_instance_2.scale = (1.0, 1.55)
### End MyScene autocode ###
