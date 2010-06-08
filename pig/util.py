"""Various ingame functions to make life easier when using pig"""

import math
import os
import sys
import traceback
from time import sleep
from inspect import isclass

import Opioid2D
from Opioid2D.public.Node import Node

import pug
from pug.util import get_package_classes, find_classes_in_module

from pig.PigDirector import PigDirector

projectPath = os.getcwd()
_revertScene = None

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
    
def save_project_settings( gameSettings):
    pug.code_export( gameSettings, "_project_settings.py", True, 
                 {'name':'project_settings'})        

def run_pig_scene( projectPath, scenename=None, position=None, resolution=None, 
                   title=None, fullscreen=None, icon='', units=None, 
                   useWorking=False):
    """run_pig_scene( ...) Run a pig scene in a game window
    
args: ( scenename, projectPath, position=None, resolution=None, 
                   title=None, fullscreen=None, icon=None, units=None, 
                   use_working=False)
All arguments with None defaults will default to info found in the 
_project_settings file unless otherwise noted.                  
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
    skip_deprecated_warnings()
    projectPath = fix_project_path(projectPath)
    if os.path.isfile(projectPath):
        projectPath = os.path.dirname(projectPath)
        if os.path.basename == 'scenes':
            projectPath = os.path.dirname(projectPath)
    set_project_path (projectPath)
    try:
        from _project_settings import project_settings
    except:
        raise ValueError("No scenes have been created yet. Run edit_project.py")
    # settings
    if position is None:
        position = project_settings.rect_opioid_window[0:2]        
    if resolution is None:
        resolution = project_settings.rect_opioid_window[2:4]
    if title is None:
        title = project_settings.title
    if fullscreen is None:
        fullscreen = project_settings.fullscreen
    if scenename is None:
        scenename = project_settings.initial_scene
        
    # get scene    
    scenedict = get_available_scenes( useWorking=useWorking)# use __Working__.py
    from pig.PigScene import PigScene
    if scenename == 'PigScene':
        from pig.PigScene import PigScene
        initial_scene = PigScene
    else:
        try:
            initial_scene = scenedict[scenename]
        except:
            if useWorking:
                module = __import__('scenes.__Working__')
                workingClasses = find_classes_in_module(module.__Working__, 
                                                        Opioid2D.Scene)
                for cls in workingClasses:
                    if cls.__name__ == scenename:
                        exec('from scenes.__Working__ import ' + scenename)
                        break
            exec('from scenes.' + scenename + ' import ' + scenename)
            raise ValueError("Problem with scene: "+scenename) 
    
    set_opioid_window_position( position)
    Opioid2D.Display.init(resolution, units, title, fullscreen, icon)
    Opioid2D.Director.start_game = True
    # Import Psyco if available
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    Opioid2D.Director.run(initial_scene)
    
def set_opioid_window_position( position):    
    if os.name == "nt":
        loc = (position[0]+5, position[1]+28)
    else:
        loc = position[0:2]
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % loc
    
def fix_project_path( path):
    """fix_project_path( path)->path after removing Idle editor info"""
    # the honest truth is that idle doesn't work for shizz with PIG.
    # but maybe someday it will... 
    
    if "idlelib" in path and "idle.py" in path:
        return sys.argv[0]
    else:
        return path

availableScenes = None
def get_available_scenes( doReload=False, useWorking=True, errors=None):
    """get_available_scenes( doReload=False, useWorking=False, errors=None)>dict
    
Get all Scenes available in modules in Scenes folder. Return dict of available 
Scene sub-classes {"sceneName":sceneClass}. PigScene is automatically included.  
doReload: if True, don't just import scene modules, but reload them
useWorking: if True, and the class in the __Working__.py file is in the class
    list, use the __Working__ scene to replace the one in the list.
errors: if a dict is passed in, it will be filled with the results of 
    sys.exc_info() for each module that had a problem being imported. Indexed
    by module
"""
    if type(errors) != type({}):
        errors=None
    global availableScenes
    if availableScenes is not None and not doReload:
        return availableScenes.copy()
    sceneList = get_package_classes('scenes', Opioid2D.Scene, doReload,
                                    errors=errors)
    # use __Working__ scene as override
    workingModule = 'scenes.__Working__'
    needsReload = workingModule in sys.modules
    sceneDict = {}
    try:
        module = __import__(workingModule)
    except ImportError:
        pass
    except:
        if getattr(Opioid2D.Director,"editorMode",False):
            if errors:
                errors[workingModule] = sys.exc_info()
        else:
            print "Exception while loading working module."
            print traceback.format_exc()
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
def get_available_objects( doReload=False, errors=None):
    """get_available_objects( doReload=False, errors=None)->dict of objects
    
Get all Nodes available in modules in Objects folder. Return a dict of available
'name':class. PigSprite is automatically included.
doReload: if True reload all object modules from disk
errors: if a dict is passed in, it will be filled with the results of 
    sys.exc_info() for each module that had a problem being imported. Indexed
    by module
"""
    global availableObjects
    if availableObjects is not None and not doReload:
        return availableObjects.copy()
    objectList = get_package_classes('objects', Node, doReload, errors=errors)
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
    if projectPath and projectPath in sys.path:
        sys.path.remove(projectPath)
    projectPath = path
    if projectPath not in sys.path:
        sys.path.insert(0,projectPath)
    os.chdir(projectPath)
        
def get_project_path():
    return projectPath
        