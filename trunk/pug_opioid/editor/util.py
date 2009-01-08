"""Various utility functions for the pug_opioid editor"""

import os.path
from inspect import getmro
import wx

import Opioid2D
from Opioid2D.public.Node import Node

from pug import code_export, GnameDropdown
from pug.syswx.util import ShowExceptionDialog
from pug.syswx.SelectionFrame import SelectionFrame
from pug.util import make_name_valid

from pug_opioid.util import get_available_scenes
from pug_opioid.editor import EditorState
from pug_opioid.editor import selectionManager

# constant to set up component agui
GNAMED_NODE = {'agui':GnameDropdown, 'aguidata':{'class_list':[Node]}}

def get_available_layers():
    """get_available_layers() -> list of available layers in Director"""
    try:
        # hide '__selections__' layer
        layers = Opioid2D.Director.scene.layers[:]
        while '__selections__' in layers:
            layers.remove('__selections__')
        return layers        
    except:
        return []
    
def get_available_groups():
    """get_available_groups() -> list of available groups in Director"""
    try:
        return Opioid2D.Director.scene._groups.keys()
    except:
        return []
    
def save_object(obj, name=None, parentWindow=None):
    """save_object(obj): Export obj as a class to objects folder

name: the name to save the object as. If not provided, a dialog will be opened
parentWindow: the parent window of name dialog. If not provided, the 
    wx.ActiveWindow will be used
"""
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
        name = make_name_valid(name)
        name = name.capitalize()
        if parentWindow == None:
            parentWindow = wx.GetActiveWindow()
        dlg = wx.TextEntryDialog( parentWindow, 
                                  "Enter the object's class/file name", 
                                  "Save Object", name)
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
    try:
        code_export( obj, path, True, {'name':objName})    
    except:
        ShowExceptionDialog
    else:
        if not obj.gname:
            obj.gname = objName
    
def save_scene():
    """Save scene to disk"""
    name = Opioid2D.Director.scene.__class__.__name__
    save_scene_as(name)
    
def save_scene_as( sceneName=None, fileName=None):#, parentWindow=None):
    """Save the current scene as a class in the scenes folder
        
sceneName: string with name to save as. If None, a dialog will be opened.
parentWindow: the parent window of name dialog. If not provided, the 
    wx.ActiveWindow will be used
"""
    scene = Opioid2D.Director.scene
    if not sceneName:
        name = scene.gname
        if not name:
            name = scene.__class__.__name__
        if name == 'PugScene' or name == 'Scene':
            name = 'MyScene'
        name = make_name_valid(name)
        name.capitalize()
        parentWindow=None
        if parentWindow == None:
            parentWindow = wx.GetActiveWindow()
        dlg = wx.TextEntryDialog( parentWindow, 
                                  "Enter the scene's class/file name", 
                                  "Save Scene", name)
        while not sceneName:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                path = os.path.join('scenes',''.join([name,'.py']))
                try:
                    file(path)
                except:
                    sceneName = name
                else:
                    confirmDlg = wx.MessageDialog( dlg, 
                           "Scene file already exists. Overwrite?",
                           "Confirm Replace",
                           wx.YES_NO | wx.NO_DEFAULT)
                    if confirmDlg.ShowModal() == wx.ID_YES:
                        sceneName = name
                    confirmDlg.Destroy()
            else:
                dlg.Destroy()
                return
        dlg.Destroy()
    if not fileName:
        fileName = sceneName
    path = os.path.join('scenes',''.join([fileName,'.py']))
    app = wx.GetApp()
    selection = app.selectedRefSet.copy()
    scene.state = None          
    wx.BeginBusyCursor()
    try:
        code_export( scene, path, True, {'name':sceneName})
    except:
        ShowExceptionDialog()
    else:
        if sceneName != Opioid2D.Director.scene.__class__.__name__:
            scenedict = get_available_scenes(True)
            loadscene = scenedict.get(sceneName, None)
            if loadscene:
                Opioid2D.Director.scene.__class__ = loadscene
                #hack
                sceneFrame = wx.GetApp().get_object_pugframe( 
                                                        Opioid2D.Director.scene)
                if sceneFrame:
                    sceneFrame.SetTitle( loadscene.__name__)
    finally:
        wx.EndBusyCursor()        
        scene.state = EditorState
        app.set_selection(selection)
    
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
            frameObj = frame.activePugWindow.objectRef()
        except:
            continue
        if isinstance(frame, SelectionFrame):
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

#hack for quitting pug when opioid quits
QUITTING = False
def project_quit(*args, **kwargs):
    """project_quit(*args, **kwargs)
    
Have the app confirm project closure.
"""
    if not wx.GetApp():
        Opioid2D.Director.realquit()
        return
    global QUITTING
    if not QUITTING:
        QUITTING = True
        app = wx.GetApp()
        if hasattr(app, '_evt_project_frame_close'):
            wx.CallAfter(app._evt_project_frame_close)
        return 
# set up our special quit
Opioid2D.Director.realquit = Opioid2D.Director.quit
Opioid2D.Director.quit = project_quit # hack to make opioid quit=pugquit        
        