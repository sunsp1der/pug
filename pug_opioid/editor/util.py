"""Various utility functions for the pug_opioid editor"""

import os.path
from inspect import getmro
import time
from copy import copy

import wx

import Opioid2D
from Opioid2D.public.Node import Node

from pug import code_export, GnameDropdown, CodeStorageExporter
from pug.syswx.util import show_exception_dialog
from pug.syswx.SelectionWindow import SelectionWindow
from pug.util import make_name_valid

from pug_opioid.util import get_available_scenes, get_available_objects
from pug_opioid.editor import EditorState

_DEBUG = True

_IMAGEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Images")
def get_image_path(filename):
    return os.path.join (_IMAGEPATH, filename)

def get_available_layers():
    """get_available_layers() -> list of available layers in Director"""
    try:
        # hide '__editor__' layer
        layers = Opioid2D.Director.scene.layers[:]
        while '__editor__' in layers:
            layers.remove('__editor__')
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
                            "\n".join([path,
                           "File already exists. Overwrite?"]),
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
        objName = name
        path = os.path.join('objects',''.join([name,'.py']))
    try:
        if getattr(obj, 'archetype', False):
            # we don't want every instance to be an archetype
            obj.archetype = False
            archetype = True
        else:
            archetype = False
        exporter = code_export( obj, path, True, {'name':objName})
        objDict = get_available_objects( True)
        if archetype:
            # return archetype status after saving
            obj.archetype = True
            oldclass = obj.__class__
            obj.__class__ = objDict[objName]
            if exporter.file_changed:
                archetype_changed( obj, oldclass, exporter)
        return exporter
    except:
        show_exception_dialog()
    
_changedArchetypeList = []    
def archetype_changed( archetype, oldclass, archetype_exporter=None):
    if archetype_exporter is None:
        archetype_exporter = CodeStorageExporter()
    newclass = archetype.__class__
    # convert all nodes referencing this archetype
    new_dummy = archetype_exporter.get_dummy(newclass)
    old_dummy = archetype_exporter.get_dummy(oldclass)
    nodes = Opioid2D.Director.scene.nodes
    storageDict = archetype_exporter.get_custom_storageDict(new_dummy)
    storageDict['as_class'] = False 
    attributeList = archetype_exporter.create_attribute_lists(
                                            new_dummy, storageDict)[0]                                                        
    for changer in nodes:
        if changer.__class__ != oldclass or changer == old_dummy:
            continue
        if _DEBUG: print "archetype_changed changer:", changer
        old_dummy = archetype_exporter.get_dummy(changer.__class__)
        changer.__class__ = newclass
        # convert the object to new archetype form
        # set attributes
        for attr in attributeList:
            try:
                oldval = getattr(old_dummy, attr)
                newval = getattr(new_dummy, attr)
            except:
                continue
            if oldval == newval or getattr(newval, '__module__', False):
                continue
            setVal = False
            try:
                val = getattr(changer, attr)
            except:
                setVal = True
            if setVal or val == oldval:
                try:
                    setattr(changer, attr, newval)
                except:
                    continue
        # set components
        oldComponents = old_dummy.components.get()
        if _DEBUG: print "archetype_changed oldComponents:", oldComponents
        newComponents = new_dummy.components.get()
        if _DEBUG: print "archetype_changed newComponents:", newComponents
        if _DEBUG: print "archetype_changed changer components:",\
                                                    changer.components.get()
        for comp in oldComponents:
            removed = changer.components.remove_duplicate_of(comp)
            if not removed:
                # if component is in new and old but not changer, don't add it!
                dupecomp = new_dummy.components.get_duplicate_of(comp)
                if dupecomp:
                    if _DEBUG: print "archetype_changed: don't add", dupecomp
                    newComponents.remove(dupecomp)
            else:
                if _DEBUG: print "archetype_changed: removed", comp

        for comp in newComponents:
            # add duplicate components
            if not changer.components.get_duplicate_of(comp):
                if _DEBUG: print "archetype_changed: add", comp
                changer.components.add(copy(comp))
    
def get_scene_errors(showDialog=True):
    """get_scene_errors(showDialog=True)->error string
    
Check the scene for probable user errors. If showDialog is False, returns a list
of errors or None if none found. If showDialog is True, brings up a dialog to
allow the user to ignore the errors. This function checks for unnamed 
archetypes, and multiple archetypes with the same name...
"""
    scene = Opioid2D.Director.scene
    errors = []
    if not scene:
        error = "No scene loaded!"
        errors.append(error)
    else:
        archetypeNames = []
        for node in scene.nodes:
            if node.archetype:
                if node.gname:
                    if node.gname in archetypeNames:
                        error = ''.join(["Duplicate archetype name: ",
                                         node.gname])
                        errors.append(error)
                    else:
                        archetypeNames.append(node.gname)
                else:
                    error = ''.join(["Unnamed archetype: class ", 
                                     node.__class__.__name__, " at ",
                                     str(node.position.x), ", ",
                                     str(node.position.y)])
                    errors.append(error)
    if errors:
        if showDialog:
            errorend = ['\nIgnore errors and save (not recommended)?']
            errormsg = '\n'.join(errors + errorend)
            dlg = wx.MessageDialog( None, errormsg, "Scene Errors",
                                    style = wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_YES:
                return None
            else:
                return errors
        else:
            return errors
    else:
        return None
    
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
    wx.GetApp().apply()
    if get_scene_errors():
        return
    if _DEBUG: print "util: save_scene_as"
    scene = Opioid2D.Director.scene
    if not sceneName:
        name = scene.gname
        if not name:
            name = scene.__class__.__name__
        if name == 'PugScene' or name == 'Scene':
            name = 'MyScene'
        name = make_name_valid(name)
        name.capitalize()
        if _DEBUG: print "util: save_scene_as 1"
        parentWindow=None
        if parentWindow == None:
            parentWindow = wx.GetActiveWindow()
        dlg = wx.TextEntryDialog( parentWindow, 
                                  "Enter the scene's class/file name", 
                                  "Save Scene", name)
        if _DEBUG: print "util: save_scene_as 2"
        while not sceneName:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                path = os.path.join('scenes',''.join([name,'.py']))
                try:
                    test = file(path)
                except:
                    sceneName = name
                else:
                    test.close()
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
    else:
        if sceneName == 'PugScene' or sceneName == 'Scene':
            save_scene_as( sceneName, fileName)
    if not fileName:
        fileName = sceneName
    path = os.path.join('scenes',''.join([fileName,'.py']))
    app = wx.GetApp()
    if _DEBUG: print "util: save_scene_as 4"
    selection = app.selectedObjectDict.keys()
    oldscene = Opioid2D.Director.scene
    wait_for_state( None)
    if _DEBUG: print "util: save_scene_as 5"
    wx.BeginBusyCursor()
    try:
        if _DEBUG: print "util: save_scene_as enter code_export"
        code_export( scene, path, True, {'name':sceneName})
        if _DEBUG: print "util: save_scene_as exit code_export"
    except:
        if _DEBUG: print "util: save_scene_as 6"        
        show_exception_dialog()
    else:
        if _DEBUG: print "util: save_scene_as 7"        
        sceneDict = get_available_scenes(True)
        Opioid2D.Director.scene.__class__ = sceneDict[sceneName]
    finally:
        wx.EndBusyCursor()        
        wait_for_state(EditorState)
        if Opioid2D.Director.scene == oldscene:
            if _DEBUG: print "util: save_scene_as reset select:", selection        
            wx.CallAfter(app.set_selection, selection)
            
def wait_for_state(state):
    "wait_for_state(state): Set scene state then wait until Opioid is ready"
    scene = Opioid2D.Director.scene
    scene.state = state
    timer = 0
    while not (scene.state == state or scene.state.__class__ == state):
        time.sleep(0.05)         
        timer += 1
        if timer > 50:
            raise ValueError("Pug unable to set scene state")
    
def close_scene_windows( scene=None):
    """_close_scene_windows( scene=None)
    
Close all scene and node windows belonging to current scene
Note: for this to work on nodes, it must be run BEFORE the scene is changed.    
"""
    if scene == None:
        scene = Opioid2D.Director.scene
    app = wx.GetApp()
    for frame in app.pugFrameDict:
        if isinstance(frame.pugWindow, SelectionWindow):
            continue
        if frame.Name == 'SceneFrame':
            continue
        try:
            frameObj = frame.pugWindow.objectRef()
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

def exporter_cleanup( exporter):
    # delete dummies from Opioid scene
    dummyDict = exporter.dummyDict
    dummyKeys = dummyDict.keys()
    for cls in dummyKeys:
        if issubclass(cls, Node):
            dummyDict[cls].delete()
    # wait for Opioid to catch up
    time.sleep(0.25)

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

#hack for making Opioid2D.Vector objects more visible
__old_repr = Opioid2D.Vector.__repr__
def __vect_repr(self):
    #old = __old_repr(self)
    return ''.join(['(', str(self.x), ', ', str(self.y),') - Opioid Vector'])     
Opioid2D.Vector.__repr__ = __vect_repr