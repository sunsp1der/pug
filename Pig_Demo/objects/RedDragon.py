### import autocode ###
from pig.Sprite import Sprite
from pug.all_components import Key_Spawn, Key_Animate_Direction
### End import autocode ###

### RedDragon autocode ###
class RedDragon(Sprite):
    layer = 'Sky'
    def on_create(self):
        self.position = (363.0, 263.0)
        self.components.add( Key_Spawn(
                spawn_object='DragonBreath',
                spawn_offset=(0.5, 0.05)) )
        self.components.add( Key_Animate_Direction(
                file='art\\dragon.png',
                grid_width=75,
                grid_height=70,
                up_frames=[(60, 70)],
                upright_frames=[(70, 80)],
                right_frames=[(0, 10)],
                downright_frames=[(10, 20)],
                down_frames=[(20, 30)],
                downleft_frames=[(30, 40)],
                left_frames=[(40, 50)],
                upleft_frames=[(50, 60)],
                rotate=True) )
### End RedDragon autocode ###
