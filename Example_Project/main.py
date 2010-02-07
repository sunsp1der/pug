import sys
from pig.util import run_pig_scene

# command line arguments
if len(sys.argv) > 1: 
    # first command line argument is used as the starting scene.
    scene = sys.argv[1] 
else:
    scene = None # use initial_scene from game_settings

run_pig_scene( __file__, scene)

# if you want to force settings manually, do something like this: 
#position = (0,0)
#resolution = (800, 600)
#title = "My Awesome Game"
#fullscreen = True
#scene = "Level 1"
#run_pig_scene( __file__, scene, position, resolution, title, fullscreen)