### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
from pug.all_components import Fade, Collision_Destroy, Grow_Shrink,\
    Key_Drive_Controls, Join_Collision_Group
### End import autocode ###

### FadeTest autocode ###
class FadeTest(PigScene):
    def on_enter(self):
        # Sprites
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art\\pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 400.0
        pigsprite_instance.position.y = 300.0
        pigsprite_instance.components.add( Fade(
                fade_in_secs=0.0) )
        pigsprite_instance.components.add( Collision_Destroy() )
        pigsprite_instance.components.add( Grow_Shrink(
                shrink_out_secs=0.0) )

        pigsprite_instance_2 = PigSprite()
        pigsprite_instance_2.image = 'art\\pug.png'
        pigsprite_instance_2.layer = 'Background'
        pigsprite_instance_2.position.x = 398.0
        pigsprite_instance_2.position.y = 387.0
        pigsprite_instance_2.components.add( Key_Drive_Controls() )
        pigsprite_instance_2.components.add( Join_Collision_Group() )
### End FadeTest autocode ###
