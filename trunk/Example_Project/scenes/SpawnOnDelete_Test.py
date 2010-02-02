"""SpawnOnDelete_Test.py"""

### import autocode ###
from objects.ExplodeParticle import ExplodeParticle
from objects.StarBomb import StarBomb
from pug.all_components import Spawn_Area
from pig.PigScene import PigScene
from pig.PigSprite import PigSprite
### End import autocode ###

### "SpawnOnDelete_Test" autocode ###
class SpawnOnDelete_Test(PigScene):
    layers = ['Background']
    def on_enter(self):
        # Archetypes
        ExplodeParticle_archetype = ExplodeParticle(gname='ExplodeParticle')
        ExplodeParticle_archetype.archetype = True

        StarBomb_archetype = StarBomb(gname='StarBomb')
        StarBomb_archetype.archetype = True

        # Sprites
        PigSprite_instance = PigSprite()
        PigSprite_instance.image = 'art/pig.png'
        PigSprite_instance.layer = 'Background'
        PigSprite_instance.position.x = 401.0
        PigSprite_instance.position.y = 551.0
        PigSprite_instance.components.add( Spawn_Area(
                object='StarBomb',
                spawn_interval=3.0,
                spawn_location='center',
                spawn_offset=(0, -1)) )
### End "SpawnOnDelete_Test" autocode ###

