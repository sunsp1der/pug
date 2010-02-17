### import autocode ###
from objects.target import target
### End import autocode ###

### startarget autocode ###
class startarget(target):
    image = 'art/explosion2.png'
    def on_create(self):
        self.position.x = 391.0
        self.position.y = 273.0
### End startarget autocode ###
