import sys
import os

import Opioid2D

from pug_opioid.util import get_available_scenes

from _game_settings import game_settings

# settings
position = game_settings.opioid_window_rect[0:2]
resolution = game_settings.opioid_window_rect[2:4]
title = game_settings.title
fullscreen = game_settings.fullscreen

    # command line arguments (sets starting scene...)
if len(sys.argv) > 1: 
    # starting scene
    # if we have a command line argument, it is used as the starting scene.
    scenedict = get_available_scenes( useWorking=True) # use __Working__.py
    initial_scene = scenedict[sys.argv[1]] 
else:
    # starting scene
    scenedict = get_available_scenes( useWorking=False)
    initial_scene = scenedict[game_settings.initial_scene]

# start Opioid
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % position
Opioid2D.Display.init(resolution, title=title, fullscreen=fullscreen)
Opioid2D.Director.start_game = True
Opioid2D.Director.run(initial_scene)