### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Set_Motion, Grow_Shrink, On_Collision_Sound,\
    Life_Zone, Fade, Stop_Motion_On_Destroy, Deals_Damage
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
                sound='sound\\beep.wav',
                their_group='target',
                my_group='bullet',
                enabled=False) )
        self.components.add( Life_Zone() )
        self.components.add( Fade(
                fade_in_secs=0.0,
                fade_out_secs=0.2) )
        self.components.add( Stop_Motion_On_Destroy() )
        self.components.add( Deals_Damage(
                damage_amount=10.0,
                destroy_on_collide=True,
                their_group='target',
                my_group='bullet') )
### End Bullet autocode ###
