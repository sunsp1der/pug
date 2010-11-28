### import autocode ###
from pig.PigScene import PigScene
from pug.all_components import Key_Sound_Scene
### End import autocode ###

### MyScene autocode ###
class MyScene(PigScene):
    def on_enter(self):
        self.components.add( Key_Sound_Scene(
                key='SPACE',
                sound='sound\\beep.wav',
                volume=0.3) )
### End MyScene autocode ###
