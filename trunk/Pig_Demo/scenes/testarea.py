### import autocode ###
from objects.testhis import testhis
from pig.PigScene import PigScene
### End import autocode ###

### testarea autocode ###
class testarea(PigScene):
    started = True

    def on_enter(self):
        # Archetypes
        testhis_archetype = testhis(gname='testhis')
        testhis_archetype.archetype = True

### End testarea autocode ###
