"""Running this file opens an Opioid2D window and an OpioidInterface to it. The
location of this file defines the root folder of the project, so keep it there.
"""
import Opioid2D 

import pug

from pug_opioid.OpioidInterface import OpioidInterface
from pug_opioid.PugScene import PugScene

class ExampleInterface(OpioidInterface):
    def __init__(self, *args, **kwargs):
        OpioidInterface.__init__(self, *args, **kwargs)
    def _post_init(self):
        # set up starting scene
        self.sceneclass = 'Diagonals'
        
        # open frame to view scene
        pug.frame(Opioid2D.Director.scene)
        
        # open frame to view first sprite in scene
        self.open_selection_frame()
    
def init_pug():
    """start mainScene with a pug interface"""  
#    Opioid2D.Display.init((800, 600), title='Scene')
#    Opioid2D.Director.run(PugScene)        
    interface = ExampleInterface(__file__)
      
if __name__ == "__main__":
    init_pug()  
