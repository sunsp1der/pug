### import autocode ###
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Scene_Timer, Grow_Shrink, Fade, Self_Destruct
### End import autocode ###

### Intro autocode ###
class Intro(Scene):
    def on_enter(self):
        self.components.add( Scene_Timer(
                scene_time=2,
                next_scene='MenuScreen') )

        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/pug.png'
        sprite_instance.layer = 'Background'
        sprite_instance.position = (400.0, 300.0)
        sprite_instance.scale = (6.0, 6.0)
        sprite_instance.components.add( Grow_Shrink(
                grow_in_secs=2.0,
                shrink_out_secs=-1.0) )
        sprite_instance.components.add( Fade(
                fade_in_secs=-1.0,
                fade_out_secs=1.0) )
        sprite_instance.components.add( Self_Destruct(
                timer_secs=1.0) )
### End Intro autocode ###
