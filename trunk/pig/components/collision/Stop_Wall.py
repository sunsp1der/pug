import Opioid2D

from pug.component import *

from pig.components.collision.Collision_Callback import Collision_Callback

class Stop_Wall( Collision_Callback):
    """Other objects stop when they collides with this object. This component is
meant to be used with a graphic that fills its area completely. For best looking
results, sprite graphics colliding with the wall should be circles."""

    @component_method
    def on_collision(self, toSprite, fromSprite, toGroup, fromGroup):
        "Push colliding object out of this sprite's area"
        delta = Opioid2D.Director.delta * 0.001
        spritepos = fromSprite.get_position()
        spritev = fromSprite.get_velocity()
        mypos = toSprite.get_position()
        for axis in [0,1]:
            if (spritepos[axis] < mypos[axis] and spritev[axis] <= 0)\
                    or (spritepos[axis] > mypos[axis] and spritev[axis] >= 0):
                # we're moving away from the wall, so let it happen
                continue
            else:
                # we need to revert to previous position
                fromSprite.position[axis] -= spritev[axis] * delta
        
register_component( Stop_Wall)