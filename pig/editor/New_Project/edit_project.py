"""Running this file opens an Opioid2D window and an OpioidInterface to it. The
location of this file defines the root folder of the project, so keep it there.
"""
import sys
import pug

from pig.editor.OpioidInterface import OpioidInterface

def init_pug():
    """start mainScene with a pug interface"""
    interface = OpioidInterface(sys.argv[0])
      
if __name__ == "__main__":
    init_pug()
