from pig.Scene import Scene
from pig import Sprite

class StartScene(Scene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        sprite_instance = Sprite()
        sprite_instance.image = 'art/pug.png'
        sprite_instance.layer = 'Background'
        sprite_instance.position.x = 400.0
        sprite_instance.position.y = 300.0  
