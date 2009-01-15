"""Various ingame functions to make life easier when using pug_opioid"""

import math
import os.path
import sys

import pug
from pug.util import get_package_classes, find_classes_in_module

import Opioid2D

projectPath = os.getcwd()
_revertScene = None

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
    Opioid2D.Director.scene.start()    
    
def save_game_settings( game_settings):
    pug.code_export( game_settings, "_game_settings.py", True, 
                 {'name':'game_settings'})            
    
def get_available_scenes( doReload=False, useWorking=True):
    """get_available_scenes( doReload=False, useWorking=False) -> dict
    
Get all Scenes available in modules in Scenes folder. Return dict of available 
Scene sub-classes {"sceneName":sceneClass}.    
doReload: if True, don't just import scene modules, but reload them
useWorking: if True, and the class in the __Working__.py file is in the class
    list, use the __Working__ scene to replace the one in the list.
"""
    sceneList = get_package_classes('scenes', Opioid2D.Scene, doReload)
    if useWorking:
        # use __Working__ scene as override
        workingModule = 'scenes.__Working__'
        needsReload = workingModule in sys.modules
        try:
            module = __import__(workingModule)
        except ImportError:
            pass
        except:
            print "Exception while loading working module."
            print sys.exc_info()[1]
            print "Using committed module instead."
        else:
            if doReload and needsReload:
                sys.modules.pop(workingModule)
                module = __import__(workingModule)
                #reload(module.__Working__)
            workingScene = find_classes_in_module(module.__Working__, 
                                                  Opioid2D.Scene)[0]
            for idx in range(len(sceneList)):
                if sceneList[idx].__name__ == workingScene.__name__:
                    global _revertScene
                    _revertScene = sceneList[idx]
                    sceneList[idx] = workingScene
    sceneDict = {}
    for item in sceneList:
        sceneDict[item.__name__]=item
    return sceneDict

def get_committed_scene():
    """get_committed_scene()->Opioid2D scene
    
The working scene normally replaces the committed disk version. This function
returns the committed version.
"""
    return _revertScene

def get_available_objects( doReload=False):
    """get_available_objects( doReload=False) -> list of Opioid2D.Nodes
    
Get all Nodes available in modules in Objects folder. Return a list of available
Node sub-classes.
doReload: if True don't just import node modules"""
    moduleList = get_package_classes('objects', Opioid2D.public.Node.Node,
                                    doReload)
    return moduleList

def set_project_path( path):
    global projectPath
    if projectPath:
        sys.path.remove(projectPath)
    projectPath = path
    if projectPath not in sys.path:
        sys.path.insert(0,projectPath)
    os.chdir(projectPath)
        
def get_project_path():
    return projectPath
    