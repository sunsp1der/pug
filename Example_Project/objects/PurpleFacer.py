"""PurpleFacer.py"""

### import autocode ###
from pug.all_components import Face_Mouse, Spawn_Area, Forward_Motion
from pig.PigSprite import PigSprite
### End import autocode ###

### "PurpleFacer" autocode ###
class PurpleFacer(PigSprite):
    image = 'art/pug.png'
    layer = 'Background'
    def on_create(self):
        self.position.x = 541.0
        self.position.y = 389.0
        self.color = (0.69999998807907104, 0.0, 1.0, 1.0)
        self.components.add( Face_Mouse() )
        self.components.add( Spawn_Area(
                object='UpFO',
                spawn_interval=0.29999999999999999,
                spawn_variance=0.0,
                spawn_location='center',
                spawn_offset=(1, 0)) )
        self.components.add( Forward_Motion(
                velocity=0))
### End "PurpleFacer" autocode ###
