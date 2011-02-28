### import autocode ###
from pig.Sprite import Sprite
from pug.all_components import Animate_Folder, On_Create_Sound
### End import autocode ###

### Explosion autocode ###
class Explosion(Sprite):
    layer = 'Background'
    def on_create(self):
        self.position = (156.0, 430.0)
        self.rotation = 180.0
        self.components.add( Animate_Folder(
                folder='art/explosion',
                mode='Stop',
                destroy=True) )
        self.components.add( On_Create_Sound(
                sound='sound/explosion.wav') )
### End Explosion autocode ###
