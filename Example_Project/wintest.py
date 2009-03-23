import sys
import os

import Opioid2D
from pug_opioid.util import get_available_scenes, set_project_path

from _game_settings import game_settings

# set this file's folder as main project path
set_project_path( os.path.dirname(sys.argv[0]))

# settings
position = game_settings.rect_opioid_window[0:2]
resolution = game_settings.rect_opioid_window[2:4]
title = game_settings.title
fullscreen = game_settings.fullscreen

    # command line arguments (sets starting scene...)
if len(sys.argv) > 1: 
    # first command line argument is used as the starting scene.
    scenedict = get_available_scenes( useWorking=True) # use __Working__.py
    initial_scene = scenedict[sys.argv[1]] 
else:
    # set starting scene to initial_scene from game_settings
    scenedict = get_available_scenes( useWorking=False)
    initial_scene = scenedict[game_settings.initial_scene]

# start Opioid
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % position
Opioid2D.Display.init(resolution, title=title, fullscreen=fullscreen, icon='')
Opioid2D.Director.start_game = True

import pug
import threading
import time
pug.frame(Opioid2D.Director)
Opioid2D.Director.run(initial_scene)

