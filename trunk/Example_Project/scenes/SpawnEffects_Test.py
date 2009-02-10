"""SpawnEffects_Test.py"""

###################
# import autocode #
###################
from objects.YellowPug import YellowPug
from pug_opioid.PugScene import PugScene
#######################
# End import autocode #
#######################

################################
# "SpawnEffects_Test" autocode #
################################
class SpawnEffects_Test(PugScene):
    layers = ['Layer 1']
    def enter(self):
        # Sprites
        yellowpug_instance = YellowPug()
        yellowpug_instance.position.x = 397.0
        yellowpug_instance.position.y = 313.0

        # Pug auto-start
        self.start()
####################################
# End "SpawnEffects_Test" autocode #
####################################

