from pig.Scene import Scene
from pig import Sprite

class StartScene(Scene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        pigsprite_instance = Sprite()
        pigsprite_instance.image = 'art/pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 400.0
        pigsprite_instance.position.y = 300.0  
