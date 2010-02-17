"""Various ingame functions to make life easier when using pig"""

import math
import os, os.path
import sys
from time import sleep
from inspect import isclass

import Opioid2D
from Opioid2D.public.Node import Node

import pug
from pug.util import get_package_classes, find_classes_in_module

from pig.PigDirector import PigDirector

projectPath = os.getcwd()
_revertScene = None

def prettify_path( path):
    "prettify_path( path)-> path with '/' as divider"
    ret = path.replace('\\','/')
    ret = ret.replace('//','/')
    return ret

def skip_deprecated_warnings():
    """skip_deprecated_warnings()

Don't display any warning messages with the word 'deprecated' in them. Opioid
has a bunch of these...
"""
    import warnings
    
    warnings.filterwarnings("ignore", message=".*deprecated.*")

def angle_to( from_position, to_position):
    """angle_to(from_position, to_position) -> angle
    
from_position and to_position in the form (x, y)
"""
    return math.degrees(math.atan2(
                            to_position[0] - from_position[0],
                            from_position[1] - to_position[1]))
    
def start_scene():
    """Start a scene running"""
    Opioid2D.Director.start_game = True
    Opioid2D.Director.scene.state = None
    # give the Director a second to pull it together
    while PigDirector.scene.state:
        sleep(0.1)
    PigDirector.scene.start()    
    
def save_game_settings( gameSettings):
    pug.code_export( gameSettings, "_game_settings.py", True, 
                 {'name':'game_settings'})        

def run_pig_scene( projectPath, scenename=None, position=None, resolution=None, 
                   title=None, fullscreen=None, icon=None, units=None, 
                   useWorking=False):
    """run_pig_scene( ...) Run a pig scene in a game window
    
args: ( scenename, projectPath, position=None, resolution=None, 
                   title=None, fullscreen=None, icon=None, units=None, 
                   use_working=False)
All arguments with None defaults will default to info found in the 
_game_settings file unless otherwise noted.                  
    projectPath: the root path of this project. If projectPath is a file path, 
                just the folder will be used. If that folder is the 'scenes'
                folder, the parent of that folder will be used.
    scenename: the name of the scene to run (look in 'scenename'.py file)
    position: (x, y) the topleft corner of the game window. 
    resolution: (x,y) the width and height of the game window
    title: the title to appear on the game window
    fullscreen: True displays game in fullscreen mode
    icon: icon graphic to use for game window
    units: viewport size in game units. Defaults to resolution
    useWorking: if True, use the __working__.py file when running the scene of 
                the same name
"""
    if os.path.isfile(projectPath):
        projectPath = os.path.dirname(projectPath)
        if os.path.basename == 'scenes':
            projectPath = os.path.dirname(projectPath)
    set_project_path (projectPath)
    from _game_settings import game_settings
    # settings
    if position is None:
        position = game_settings.rect_opioid_window[0:2]        
    if resolution is None:
        resolution = game_settings.rect_opioid_window[2:4]
    if title is None:
        title = game_settings.title
    if fullscreen is None:
        fullscreen = game_settings.fullscreen
    if scenename is None:
        scenename = game_settings.initial_scene
        
    # get scene    
    scenedict = get_available_scenes( useWorking=useWorking)# use __Working__.py
    initial_scene = scenedict[scenename] 
    
    icon = ''
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % position
    Opioid2D.Display.init(resolution, units, title, fullscreen, icon)
    Opioid2D.Director.start_game = True
    Opioid2D.Director.run(initial_scene)

availableScenes = None
def get_available_scenes( doReload=False, useWorking=True):
    """get_available_scenes( doReload=False, useWorking=False) -> dict
    
Get all Scenes available in modules in Scenes folder. Return dict of available 
Scene sub-classes {"sceneName":sceneClass}. PigScene is automatically included.  
doReload: if True, don't just import scene modules, but reload them
useWorking: if True, and the class in the __Working__.py file is in the class
    list, use the __Working__ scene to replace the one in the list.
"""
    global availableScenes
    if availableScenes is not None and not doReload:
        return availableScenes.copy()
    sceneList = get_package_classes('scenes', Opioid2D.Scene, doReload)
    # use __Working__ scene as override
    workingModule = 'scenes.__Working__'
    needsReload = workingModule in sys.modules
    sceneDict = {}
    try:
        module = __import__(workingModule)
    except ImportError:
        pass
    except:
        print "Exception while loading working module."
        print sys.exc_info()[1]
    else:
        if doReload and needsReload:
            sys.modules.pop(workingModule)
            module = __import__(workingModule)
            #reload(module.__Working__)
        classes = find_classes_in_module(module.__Working__, Opioid2D.Scene)
        if classes:
            workingScene = classes[0]
            if useWorking:
                for idx in range(len(sceneList)):
                    if sceneList[idx].__name__ == workingScene.__name__:
                        global _revertScene
                        _revertScene = sceneList[idx]
                        sceneList[idx] = workingScene
                        break
            else:
                sceneDict['__Working__'] = workingScene
        else:
            print "No scene in working module.", \
                    "Using committed module instead."
    for item in sceneList:
        sceneDict[item.__name__]=item
    availableScenes = sceneDict.copy()
    return sceneDict

def get_committed_scene():
    """get_committed_scene()->Opioid2D scene
    
The working scene normally replaces the committed disk version. This function
returns the committed version.
"""
    return _revertScene

availableObjects = None
def get_available_objects( doReload=False):
    """get_available_objects( doReload=False) -> list of Opioid2D.Nodes
    
Get all Nodes available in modules in Objects folder. Return a dict of available
'name':class. PigSprite is automatically included.
doReload: if True reload all object modules from disk"""
    global availableObjects
    if availableObjects is not None and not doReload:
        return availableObjects.copy()
    objectList = get_package_classes('objects', Node, doReload)
    objectDict = {}
    for item in objectList:
        objectDict[item.__name__]=item
    availableObjects = objectDict.copy()
    return objectDict

def get_project_object( obj, reload=False, accept_class=True):
    """get_project_object(object, reload=False, accept_class=True)
    
reload: reload project objects
accept_class: object can be a class, which will simply be returned
    
A utility function mainly for components. Converts a string into a class from
the objects folder."""
    if isclass(obj) and accept_class:
        return obj
    objDict = get_available_objects(reload)
    if obj in objDict:
        return objDict[obj]
    return None
    

def set_project_path( path):
    global projectPath
    path = os.path.realpath(path)
    if projectPath:
        sys.path.remove(projectPath)
    projectPath = path
    if projectPath not in sys.path:
        sys.path.insert(0,projectPath)
    os.chdir(projectPath)
        
def get_project_path():
    return projectPath
        