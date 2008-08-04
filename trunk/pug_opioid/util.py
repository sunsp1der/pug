"""Various utility functions for pug_opioid"""
import os.path
import sys
from inspect import getmro
import wx

import Opioid2D

from pug import code_export
from pug.util import get_folder_classes

projectPath = os.getcwd()

def get_available_layers():
    """get_available_layers() -> list of available layers in Director"""
    try:
        return Opioid2D.Director.scene.layers
    except:
        return []
    
def get_available_groups():
    """get_available_groups() -> list of available groups in Director"""
    try:
        return Opioid2D.Director.scene._groups.keys()
    except:
        return []
    
def get_available_scenes( doReload=False):
    """get_available_scenes( doReload=False) -> list of Opioid2D.Scenes
    
Get all Scenes available in modules in Scenes folder. Return list of available 
Scene sub-classes.    
doReload: if True, don't just import scene modules, but reload them"""
    sceneFolder = os.path.join(projectPath,'scenes')
    sceneList = get_folder_classes(sceneFolder, Opioid2D.Scene, doReload)
    return sceneList

def get_available_objects( doReload=False):
    """get_available_objects( doReload=False) -> list of Opioid2D.Nodes
    
Get all Nodes available in modules in Objects folder. Return a list of available
Node sub-classes.
doReload: if True don't just import node modules"""
    moduleFolder = os.path.join(projectPath,'objects')
    moduleList = get_folder_classes(moduleFolder, Opioid2D.public.Node.Node,
                                    doReload)
    return moduleList

def set_project_path( path):
    global projectPath
    projectPath = path
    if projectPath not in sys.path:
        sys.path.insert(0,projectPath)
    os.chdir(projectPath)
        
def get_project_path():
    return projectPath

def save_object(obj, name = None):
    """save_object(obj): Export obj as a class to objects folder"""
    if not isinstance(obj, Opioid2D.public.Node.Node):
        raise TypeError('save_object() arg 1 must be a Node')
    if not name:
        name = obj.gname
        if not name:
            name = obj.__class__.__name__
        # we generally don't want to save with the same name as 
        # a base class of the same object
        superclasses = getmro(obj.__class__)[1:]
        for cls in superclasses:
            if name == cls.__name__:
                name = ''.join(['My',name])
        dlg = wx.TextEntryDialog( None, "Enter the object's class/file name", 
                                  "Enter name", name)
        objName = ''
        while not objName:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                path = os.path.join('objects',''.join([name,'.py']))
                try:
                    file(path)
                except:
                    objName = name
                else:
                    confirmDlg = wx.MessageDialog( dlg, 
                           "Object file already exists. Overwrite?",
                           "Confirm Replace",
                           wx.YES_NO | wx.NO_DEFAULT)
                    if confirmDlg.ShowModal() == wx.ID_YES:
                        objName = name
                    confirmDlg.Destroy()
            else:
                dlg.Destroy()
                return
        dlg.Destroy()
    else:
        path = os.path.join('objects',''.join([name,'.py']))
    code_export( obj, path, True, {'name':objName})    
        
def close_scene_windows( scene=None):
    """_close_scene_windows( scene=None)
    
Close all scene and node windows belonging to current scene
Note: for this to work on nodes, it must be run BEFORE the scene is changed.    
"""
    if scene == None:
        scene = Opioid2D.Director.scene
    app = wx.GetApp()
    for frame in app.pugFrameDict:
        try:
            frameObj = frame.objectRef()
        except:
            continue
        doclose = False
        if frameObj == scene:
            doclose = True
        else:
            if isinstance(frameObj, Opioid2D.public.Node.Node):
                try:
                    nodescene = frameObj.layer._scene
                except:
                    nodescene = 0
                if nodescene == scene:
                    doclose = True
        if doclose:
            frame.Close()
        