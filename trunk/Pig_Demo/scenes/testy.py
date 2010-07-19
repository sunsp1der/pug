### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Textbox
### End import autocode ###

### testy autocode ###
class testy(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (400.0, 300.0)
        pigsprite_instance.components.add( Textbox(
                text='texeeeee awoioiedoide',
                max_width=50) )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position = (386.0, 277.0)
        pigsprite_instance_2.components.add( Textbox(
                text='texeeeee') )
### End testy autocode ###
