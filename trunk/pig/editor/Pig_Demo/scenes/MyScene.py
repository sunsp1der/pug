### import autocode ###
from pig.Scene import Scene
from pig.Sprite import Sprite
### End import autocode ###

### MyScene autocode ###
class MyScene(Scene):
    layers = ['fork', 'Background']

    def on_enter(self):
        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/pug.png'
        sprite_instance.layer = 'fork'
        sprite_instance.position = (400.0, 300.0)
        sprite_instance.tint = (255, 0, 0)

        sprite_instance_2 = Sprite()
        sprite_instance_2.image = 'art/pug.png'
        sprite_instance_2.layer = 'Background'
        sprite_instance_2.position = (420.0, 320.0)
        sprite_instance_2.tint = (0, 0, 255)

        fred = Sprite(gname='fred')
        fred.image = 'art/pug.png'
        fred.layer = 'Background'
        fred.position = (410.0, 310.0)
### End MyScene autocode ###
