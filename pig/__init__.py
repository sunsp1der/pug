"""Python Inventor Gizmo"""

import util # must be first

from Sprite import Sprite
from Scene import Scene
from PigDirector import PigDirector as Director
from PauseState import PauseState

from gamedata import get_gamedata

import components 
import keyboard
import audio

from create_project import create_project as do_create_project
from create_demo_project import create_demo_project as do_create_demo_project
create_project = do_create_project
create_demo_project = do_create_demo_project