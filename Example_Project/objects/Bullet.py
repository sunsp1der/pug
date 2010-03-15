### import autocode ###
from pig.PigSprite import PigSprite
from pug.all_components import Set_Motion, Grow_Shrink, Collision_Destroy,\
    On_Collision_Sound, Life_Zone, Join_Group
### End import autocode ###

### Bullet autocode ###
class Bullet(PigSprite):
    image = 'art\\pig.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 137.0
        self.position.y = 501.0
        self.scale.x = 0.20000000298023224
        self.scale.y = 0.20000000298023224
        self.color = (0.0, 1.0, 0.0, 1.0)
        self.components.add( Set_Motion(
                velocity_y=-500) )
        self.components.add( Grow_Shrink(
                grow_in_secs=0.2,
                shrink_out_secs=-1.0) )
        self.components.add( Collision_Destroy(
                with_group='target',
                my_group='bullet') )
        self.components.add( On_Collision_Sound(
                sound='sounds\\snap.wav',
                with_group='target',
                my_group='FANCY') )
        self.components.add( Life_Zone() )
        self.components.add( Join_Group(
                group='org') )
### End Bullet autocode ###