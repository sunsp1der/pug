### import autocode ###
from objects.ShipSprite import ShipSprite
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Keyboard_Direction_Controls
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art/pig.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 400.0
        pigsprite_instance.position.y = 300.0
        pigsprite_instance.color = (0.0, 1.0, 1.0, 1.0)

        shipsprite_instance = ShipSprite()
        shipsprite_instance.position.x = 342.0
        shipsprite_instance.position.y = 146.0
        shipsprite_instance.components.add( Keyboard_Direction_Controls() )
### End MyScene autocode ###
