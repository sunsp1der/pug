from pig.PigScene import PigScene
from pig import PigSprite

class StartScene(PigScene):
    layers = ['Background']
    def on_enter(self):
#        # Sprites
        from pig import PigSprite
        pigsprite_instance = PigSprite()
        pigsprite_instance.image = 'art/pug.png'
        pigsprite_instance.layer = 'Background'
        pigsprite_instance.position.x = 400.0
        pigsprite_instance.position.y = 300.0  
        pigsprite_instance.delete()       
