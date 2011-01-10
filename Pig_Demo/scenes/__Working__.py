### import autocode ###
from pig.Scene import Scene
from pig.Sprite import Sprite
from pug.all_components import Textbox
### End import autocode ###

### MyScene autocode ###
class MyScene(Scene):
    _Scene__node_num = 2
    def on_enter(self):
        # Sprites
        sprite_instance = Sprite()
        sprite_instance.layer = 'Background'
        sprite_instance.position = (182.0, 83.0)
        sprite_instance.scale = (7.75, 9.147)
        sprite_instance.components.add( Textbox(
                text='ore') )

        sprite_instance_2 = Sprite()
        sprite_instance_2.image = 'art\\pug.png'
        sprite_instance_2.layer = 'Background'
        sprite_instance_2.position = (461.0, 376.25)
        sprite_instance_2.scale = (1.0, 1.55)
### End MyScene autocode ###
