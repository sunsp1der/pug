### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Set_Motion, Grow_Shrink, On_Collision_Sound,\
    Life_Zone, Fade, Collision_Destroy, Stop_Motion_On_Destroy
### End import autocode ###

### Bullet autocode ###
class Bullet(PigSprite):
    image = 'art\\pug.png'
    layer = 'Background'
    def on_create(self):
        self.position = (316.0, 531.0)
        self.scale = (0.20000000298023224, 0.20000000298023224)
        self.tint = (33, 210, 23)
        self.components.add( Set_Motion(
                velocity_y=-500) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.2,
                shrink_out_secs=-1.0) )
        self.components.add( On_Collision_Sound(
                sound='sound\\snap.wav',
                with_group='target',
                my_group='bullet') )
        self.components.add( Life_Zone() )
        self.components.add( Fade(
                fade_in_secs=0.0,
                fade_out_secs=0.2) )
        self.components.add( Collision_Destroy(
                with_group='target',
                my_group='bullet') )
        self.components.add( Stop_Motion_On_Destroy() )
### End Bullet autocode ###
