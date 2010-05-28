import sys
import _pythonpather
from pig.util import run_pig_scene

# command line arguments
if len(sys.argv) > 1: 
    # first command line argument is used as the starting scene.
    scene = sys.argv[1] 
else:
    scene = None # use initial_scene from project_settings

run_pig_scene( __file__, scene)

