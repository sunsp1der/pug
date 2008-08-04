"""Running this file opens an Opioid2D window and an OpioidInterface to it. The
location of this file defines the root folder of the project, so keep it there.
"""
import Opioid2D 

from pug_opioid.OpioidInterface import OpioidInterface
from pug_opioid.PugScene import PugScene

def init_pug():
    """start mainScene with a pug interface"""  
    interface = OpioidInterface(__file__)
    Opioid2D.Display.init((800, 600), title='Scene')
    Opioid2D.Director.run(PugScene)        
      
if __name__ == "__main__":
    init_pug()  