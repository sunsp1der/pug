"""MouseFaceFollow_Test.py"""

### import autocode ###
from objects.ShipSprite import ShipSprite
from objects.YellowPug import YellowPug
from pig.PigScene import PigScene
from pug.all_components import Follow_Mouse, Face_Object, Face_Mouse,\
    Keys_Velocity
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
        shipsprite_instance.components.add( Follow_Mouse() )
        shipsprite_instance.components.add( Face_Object(
                target='mouse pointer',
                offset=-90) )

        mouse_pointer = YellowPug(gname='mouse pointer')
        mouse_pointer.position.x = 373.0
        mouse_pointer.position.y = 286.0
        mouse_pointer.components.add( Face_Mouse() )
        mouse_pointer.components.add( Keys_Velocity(
                velocity_y=100,
                up_key=119,
                down_key=115,
                left_key=97,
                right_key=100) )
### End MouseFaceFollow_Test autocode ###
