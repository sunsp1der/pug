#1

### import autocode ###
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

#2

### testrite autocode ###
class testrite(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Sprites
        pass
        PigSprite_instance = PigSprite()
        PigSprite_instance.image = 'art/pig.png'
        PigSprite_instance.layer = 'Background'
        PigSprite_instance.position.x = 243.0
        PigSprite_instance.position.y = 169.0
### End testrite autocode ###

