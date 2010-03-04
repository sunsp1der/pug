"""MouseFaceFollow_Test.py"""

### import autocode ###
from objects.ShipSprite import ShipSprite
from objects.YellowPug import YellowPug
from pig.PigScene import PigScene
from pug.all_components import Mouse_Follow, Face_Object, Mouse_Face
### End import autocode ###

### MouseFaceFollow_Test autocode ###
class MouseFaceFollow_Test(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Archetypes
        YellowPug_archetype = YellowPug(gname='YellowPug')
        YellowPug_archetype.archetype = True

        # Sprites
        shipsprite_instance = ShipSprite()
        shipsprite_instance.components.add( Mouse_Follow() )
        shipsprite_instance.components.add( Face_Object(
                target='mouse pointer',
                offset=-90) )

        mouse_pointer = YellowPug(gname='mouse pointer')
        mouse_pointer.position.x = 436.0
        mouse_pointer.position.y = 247.0
        mouse_pointer.components.add( Mouse_Face() )
### End MouseFaceFollow_Test autocode ###
