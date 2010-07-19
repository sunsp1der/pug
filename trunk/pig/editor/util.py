"""Various utility functions for the pig editor"""

import os.path
from inspect import getmro
import time
from copy import copy
import shutil

import wx

import Opioid2D
from Opioid2D.public.Node import Node
from Opioid2D.public.Vector import VectorReference
from Opioid2D.public.Image import ImageInstance

import pug
from pug import code_export, CodeStorageExporter
from pug.component import Component
from pug.syswx.util import show_exception_dialog
from pug.syswx.SelectionWindow import SelectionWindow
from pug.util import make_valid_attr_name, python_process

from pig.util import get_available_scenes, get_available_objects, \
                        get_project_path
from pig.editor import EditorState
from pig.PigDirector import PigDirector

_DEBUG = False

_IMAGEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Images")
def get_image_path(filename):
    return os.path.join (_IMAGEPATH, filename)

# art file extensions in common between wx and opioid/pygame
_fl_art_types =(
            # display, filter
            ("All supported formats", "All"),
            ("BMP (*.bmp)", "*.bmp"),
            ("GIF (*.gif)", "*.gif"),
            ("PNG (*.png)", "*.png"),
            ("JPEG (*.jpg)", "*.jpg"),
            ("PCX (*.pcx)", "*.pcx"),
            ("TIFF (*.tif)", "*.tif"),
            ("All Files", "*.*"),
            )

def get_available_layers():
    """get_available_layers() -> list of available layers in Director"""
    try:
        # hide '__editor__' layer
        layers = PigDirector.scene.layers[:]
        while '__editor__' in layers:
            layers.remove('__editor__')
        return layers        
    except:
        return []
    
def test_scene_code(scenename):
    """test_scene_code( scenename)

This method tests a scene's code (including the enter function) without actually
loading it into view. It is meant to be used in a try clause and will raise the
exception that caused the scene to fail.    

scenename: name of scene to test
"""
    if scenename == 'PigScene':
        # we'll assume PigScene is okay
        return
    if wx.GetApp() and wx.GetApp().get_project_object():
        wx.GetApp().get_project_object().reload_object_list()
    else:
        get_available_objects(True)
    exec('import scenes.' + scenename + ' as reload_module')
    reload(reload_module)
    exec('from scenes.'+scenename+' import '+scenename+' as scene')
    test = scene()
    try:
        test.enter()
    except:
        # for some reason, if we don't do the following, images get broken
        Opioid2D.ResourceManager.clear_cache()
        raise
    else:
        # for some reason, if we don't do the following, images get broken
        Opioid2D.ResourceManager.clear_cache()
        
    
def get_available_groups():
    """get_available_groups() -> list of available groups in Director"""
    try:
        return PigDirector.scene._groups.keys()
    except:
        return []

def create_new_project(project_path=None):
    "create_new_project(project_path=None)->if successful, returns project_path"
    if not project_path:
        this_folder = os.path.split( os.path.abspath(__file__))[0]
        source = os.path.join( this_folder, "New_Project")
        parent = wx.GetApp().get_project_frame()
        dlg = wx.TextEntryDialog( parent,
                                  "Project Name",
                                  "Create New Project", 
                                  "My Project")
        if dlg.ShowModal() != wx.ID_OK:
            return
        new_project_name = dlg.GetValue()
        dlg.Destroy()
        dlg = wx.DirDialog( parent, "Create project in folder:",
                            style=wx.DD_DEFAULT_STYLE )
        if dlg.ShowModal() != wx.ID_OK:
            return
        dest_folder = dlg.GetPath()
        project_path = os.path.join( dest_folder, new_project_name)
        dlg.Destroy()
    try:
        shutil.copytree(source, project_path)
        create_pythonpather( project_path)
    except:
        show_exception_dialog()          
        return  
    return project_path

def create_pythonpather( path):
    filename = os.path.join( path, '_pythonpather.py')
    pp_file = open( filename, 'w')
    pp_code = """# This file makes sure adds pig and pug to the search path
    
try:
    import sys
    sys.path.append('""" + os.path.split(pug.__path__[0])[0]+"""')
except:
    pass
"""
    pp_file.write( pp_code)
    pp_file.close

def open_project( project_path=None, force=False, quit=True): 
    """open_project( project_path=None, force=False, quit=True)->True if openned
    
project_path: the main folder of the projet to open
force: if True, don't ask the user if they want to save current file
quit: if True, quit the current project after opening new one. 
"""
    interface = wx.GetApp().get_project_object()
    if interface and not force and not interface._pre_quit_func():
            return
    if not project_path:
        if interface:
            parent = wx.GetApp().get_project_frame()
        else:
            parent = None
        dlg = wx.DirDialog( parent, "Select project folder:",
                            style=wx.DD_DEFAULT_STYLE )
        if dlg.ShowModal() != wx.ID_OK:
            return
        project_path = dlg.GetPath()
        dlg.Destroy()
    project_editor = os.path.join( project_path, "edit_project.py")
    if not os.path.isfile( project_editor):
        wx.MessageDialog( wx.GetApp().get_project_frame(),
                    'File edit_project.py not found in ' + project_path,
                    'Invalid Project Folder',
                    wx.OK | wx.ICON_INFORMATION)
        return False        
    if interface and quit:
        interface.quit( False)
    python_process(project_editor)
    return True

def save_object(obj, name=None, parentWindow=None):
    """save_object(obj): Export obj as a class to objects folder

name: the name to save the object as. If not provided, a dialog will be opened
parentWindow: the parent window of name dialog. If not provided, the 
    wx.ActiveWindow will be used
"""
    if not isinstance(obj, Node):
        raise TypeError('save_object() arg 1 must be a Node')
    if not name:
        if obj.archetype:
            name = obj.gname
        else:
            if obj.gname:
                name = obj.gname+"Class"
            else:
                name = "MyClass"
        if not name:
            name = obj.__class__.__name__
        if parentWindow == None:
            parentWindow = wx.GetActiveWindow()
        objName = ''
        # we generally don't want to save with the same name as 
        # a base class of the same object
        superclasses = getmro(obj.__class__)[1:]
        for cls in superclasses:
            if name == cls.__name__ or name=='Sprite' or name=='PigSprite':
                name = ''.join(['My',name])
                break
        dlg = wx.TextEntryDialog( parentWindow, 
                                  "Enter the object's class/file name", 
                                  "Save Object", name)
        name = make_valid_attr_name(name)
        while not objName:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                if name == 'PigSprite' or name == 'Sprite':
                    errorDlg = wx.MessageDialog( dlg, 
                           "You can't use the names 'PigSprite' or 'Sprite'",
                           "Reserved Name",
                           wx.OK)
                    errorDlg.ShowModal()
                    errorDlg.Destroy() 
                    dlg.SetValue('MySprite')
                    dlg.SetFocus()      
                    continue                
# DECIDED TO REMOVE THE OVERWRITE CONFIRM DIALOG                
#                try:
#                    file(path)
#                except:
#                    objName = name
#                else:
#                    confirmDlg = wx.MessageDialog( dlg, 
#                            "\n".join([path,
#                           "File already exists. Overwrite?"]),
#                           "Confirm Replace",
#                           wx.YES_NO | wx.NO_DEFAULT)
#                    if confirmDlg.ShowModal() == wx.ID_YES:
#                        objName = name
#                    confirmDlg.Destroy()
# INSTEAD JUST USE NAME
                objName = name
                path = os.path.join('objects',''.join([name,'.py']))
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
        try: 
            pigsprite = PigSprite
        except:
            from pig.PigSprite import PigSprite
        exporter = code_export( obj, path, True, {'name':objName,
                                                  'base_class':PigSprite})
        objDict = get_available_objects( True)
        oldclass = obj.__class__
        if oldclass != objDict[objName]:
            obj.__class__ = objDict[objName]            
        if archetype:
            # return archetype status after saving
            obj.archetype = True
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
    nodes = PigDirector.scene.nodes
    storageDict = archetype_exporter.get_custom_storageDict(new_dummy)
    storageDict['as_class'] = False 
    attributeList = archetype_exporter.create_attribute_lists(
                                            new_dummy, storageDict)[0]                                                        
    for changer in nodes:
        if changer == old_dummy or changer == new_dummy or changer == archetype:
            # just a temporary object used by this process
            continue
        if not (changer.__class__.__name__ == newclass.__name__ and \
                    changer.__class__.__module__ == newclass.__module__):
            # not of the archetype's class
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
            if oldval == newval:
                continue
            setVal = False
            try:
                val = getattr(changer, attr)
            except:
                setVal = True
            if getattr(newval, '__module__', False):
                valtype = type(newval)
                if valtype == VectorReference:
                    setVal = val.x == oldval.x and val.y == oldval.y
                elif valtype == ImageInstance:
                    setVal = True
                else:
                    continue
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
    scene = PigDirector.scene
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
            dlg = wx.MessageDialog( wx.GetApp().get_project_frame(), errormsg, 
                                    "Scene Errors",
                                    style = wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_YES:
                return None
            else:
                return errors
        else:
            return errors
    else:
        return None

_filetypes = [
             ['art',['jpg','png','gif','bmp','pcx','tif','ttf']],
             ['sound',['wav']],
             ]
def on_drop_files( x, y, filenames): 
    types = _filetypes[:]
    for type in types:
        type.append([])
    unknown = []
    for filename in filenames:
        splitname = filename.rsplit('.',1)
        typefound = False
        if len(splitname) == 1:
            unknown.append(filename)
            continue
        for type in types:
            if splitname[1].lower() in type[1]:
                type[2].append(filename)
                typefound = True
                break
        if not typefound:
            unknown.append(filename)
    projectPath = get_project_path()
    if len(filenames) - len(unknown) == 1:
        filename = filenames[0]
        dest = projectPath
        if unknown:
            return ([])
        for type in types:
            if type[2]:
                title = "Copy "+type[0]+" into project" 
                dest = os.path.join(dest, type[0], os.path.split(filename)[1])
        dlg = wx.MessageDialog( wx.GetApp().get_project_frame(),
                    "Copy file:\n"+filename+"\nto:\n"+dest+"?\n\n"+\
                    "If file exists, it will be overwritten.",
                    title, wx.YES_NO | wx.ICON_QUESTION)
        wx.GetApp().raise_all_frames()
        if dlg.ShowModal() == wx.ID_YES:
            try:
                shutil.copyfile(filename, dest)
            except:
                show_exception_dialog()
        return [dest]
    else:
        title = "Copy multiple files into project"
        message = ""
        copies = []
        for type in types:
            if not type[2]:
                continue
            message += "Copy "+type[0]+" files:\n\n"
            for filename in type[2]:
                dest = os.path.join(projectPath, type[0], 
                                    os.path.split(filename)[1])
                message += "> "+filename+" to "+dest+"\n"
                copies += (filename,dest)
            message += "\n"
        message += "If files exist, they will be overwritten."
        dlg = wx.MessageDialog( wx.GetApp().get_project_frame(),
                    message, title, wx.YES_NO | wx.ICON_QUESTION)
        wx.GetApp().raise_all_frames()
        copied = []
        if dlg.ShowModal() == wx.ID_YES:
            for filename, dest in copies:
                try:                
                    shutil.copyfile(filename, dest)
                except:
                    show_exception_dialog()
                else:
                    copied.append(dest)
        return copied

def save_scene():
    """Save scene to disk"""
    name = PigDirector.scene.__class__.__name__
    return save_scene_as(name)
        
def save_scene_as( sceneName=None, fileName=None):#, parentWindow=None):
    """save_scene_as( sceneName=None, fileName=None)->Filename or False if fail 
    Save the current scene as a class in the scenes folder
        
sceneName: string with name to save as. If None, a dialog will be opened.
parentWindow: the parent window of name dialog. If not provided, the 
    wx.ActiveWindow will be used
"""
    wx.GetApp().apply()
    if get_scene_errors():
        return False
    if _DEBUG: print "util: save_scene_as"
    scene = PigDirector.scene
    if not sceneName:
        name = scene.__class__.__name__
        if name == 'PigScene' or name == 'Scene':
            name = 'MyScene'
        name = make_valid_attr_name(name)
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
                name = make_valid_attr_name(str(dlg.GetValue()))
                if name == 'PigScene' or name == 'Scene':
                    errorDlg = wx.MessageDialog( dlg, 
                           "You can't use the names 'PigScene' or 'Scene'",
                           "Reserved Name",
                           wx.OK)
                    errorDlg.ShowModal()
                    errorDlg.Destroy() 
                    dlg.SetValue('MyScene')
                    dlg.SetFocus()      
                    continue
# DECIDED TO REMOVE THE OVERWRITE CONFIRM DIALOG
#                try:
#                    test = file(path)
#                except:
#                    sceneName = name
#                else:
#                    test.close()
#                    confirmDlg = wx.MessageDialog( dlg, 
#                           "Scene file already exists. Overwrite?",
#                           "Confirm Replace",
#                           wx.YES_NO | wx.NO_DEFAULT)
#                    if confirmDlg.ShowModal() == wx.ID_YES:
#                        sceneName = name
#                    confirmDlg.Destroy()       
# INSTEAD JUST USE NAME
                sceneName = name             
                path = os.path.join('scenes',''.join([name,'.py']))
            else:
                dlg.Destroy()
                return False
        dlg.Destroy()
    else:
        if sceneName == 'PigScene' or sceneName == 'Scene':
            raise ValueError("Can't save over 'PigScene' or 'Scene'")
#            save_scene_as( sceneName, fileName)
    if not fileName:
        fileName = ''.join([sceneName, '.py'])
    path = os.path.join('scenes',fileName)
    app = wx.GetApp()
    if _DEBUG: print "util: save_scene_as 4"
    selection = app.selectedObjectDict.keys()
    oldscene = PigDirector.scene
    wait_for_state( None)
    if _DEBUG: print "util: save_scene_as 5"
    wx.BeginBusyCursor()
    saved = False
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
        PigDirector.scene.__class__ = sceneDict[sceneName]
        saved = True
    finally:
        wx.EndBusyCursor()        
        if PigDirector.scene != oldscene:
            wx.GetApp().set_selection([])
            if _DEBUG: print "util: save_scene_as reset select:", selection        
        wait_for_state(EditorState)

        wx.GetApp().refresh()
    if saved:
        return fileName
    else:
        return False
          
def wait_for_state(state):
    "wait_for_state(state): Set scene state then wait until Opioid is ready"
    scene = PigDirector.scene
    oldstate = scene.state
    scene.state = state
    timer = 0
    while not (scene.state == state or scene.state.__class__ == state) and \
            getattr(oldstate, 'exitted', True):
        if _DEBUG: print "   Waiting for state: ",state
        time.sleep(0.05)         
        timer += 1
        if timer > 50:
            raise ValueError("Pug unable to set scene state")
    if _DEBUG: print "   State set"

def wait_for_exit_scene():  
    PigDirector.scene.exit()
    while not PigDirector.scene.exitted:
        time.sleep(0.05) # give Opioid time to stop
    
def close_scene_windows( scene=None):
    """_close_scene_windows( scene=None)
    
Close all scene and node windows belonging to current scene
Note: for this to work on nodes, it must be run BEFORE the scene is changed.    
"""
    if scene == None:
        scene = PigDirector.scene
    app = wx.GetApp()
    for frame in app.pugFrameDict:
        if not bool(frame) or isinstance(frame.pugWindow, SelectionWindow):
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
        elif isinstance(frameObj, Node):
            try:
                nodescene = frameObj.layer._scene
            except:
                nodescene = 0
            if nodescene == scene:
                doclose = True
        elif isinstance(frameObj, Component):
            if _DEBUG: print "close_scene_windows: Componentframe"
            if _DEBUG: print "   frameObj:", frameObj
            if _DEBUG: print "   owner:", frameObj.owner
            if not frameObj.owner:
                doclose = True
            else:
                if isinstance(frameObj.owner, Node):
                    try:
                        nodescene = frameObj.owner.layer_scene
                    except:
                        nodescene = scene
                    if _DEBUG: print "   scene:", nodescene
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

#hack for making Opioid2D.Vector objects more visible
__old_repr = Opioid2D.Vector.__repr__
def __vect_repr(self):
    #old = __old_repr(self)
    return ''.join(['(', str(self.x), ', ', str(self.y),') - Opioid Vector'])     
Opioid2D.Vector.__repr__ = __vect_repr