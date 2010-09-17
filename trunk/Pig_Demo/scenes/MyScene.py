### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Utility_Keys, Animate
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def __init__(self, *args, **kwargs):
        PigScene.__init__(self, *args, **kwargs)
        self.components.add( Utility_Keys() )

    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'C:\\Users\\idelsol\\Documents\\My Code\\Pig_Pug\\Pig_Demo\\art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position = (307.0, 197.0)
        pigsprite_instance.components.add( Animate(
                folder='art\\explosion',
                fps=30,
                mode='Repeat') )
### End MyScene autocode ###
