"""Various utility functions for the pig editor"""

import time
import shutil

import wx

import Opioid2D
from Opioid2D.public.Node import Node

import pug
from pug.component import Component
from pug.syswx.util import show_exception_dialog
from pug.syswx.SelectionWindow import SelectionWindow
from pug.util import python_process, edit_process

from pig.util import get_project_path
from pig.editor.storage import * # included as a convenience

_DEBUG = False

_IMAGEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Images")
def get_image_path(filename):
    return os.path.join (_IMAGEPATH, filename)

# art file extensions in common between wx and opioid/pygame
# formatted for use with wx imagebrowser
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

def edit_project_file():
    """edit_project_file(): browse for a file to edit"""
    cwd = os.getcwd() # save this for later
    dlg = wx.FileDialog(
        wx.GetApp().get_project_frame(), 
        message="Choose a file to edit",
        defaultDir=cwd,
        wildcard="Python files (*.py)|*.py",
        style=wx.OPEN | wx.CHANGE_DIR
        )
    if dlg.ShowModal() == wx.ID_OK:
        file = dlg.GetPath()
        if file:
            edit_process(file)
        dlg.Destroy()
    os.chdir(cwd) # thanks for automatically changing that, windows
    

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
        
def test_scene_code(scenename, modulename = None):
    """test_scene_code( scenename)

This method tests a scene's code (including the enter function) without actually
loading it into view. It is meant to be used in a try clause and will raise the
exception that caused the scene to fail.    

scenename: name of scene to test
modulename: name of module to find scene in. Basically for __Working__ only
"""
    _DEBUG = False #
    if modulename is None:
        modulename = scenename
    if _DEBUG: print "test_scene_code 1"
    if scenename == 'PigScene':
        # we'll assume PigScene is okay
        return
    if wx.GetApp() and wx.GetApp().get_project_object():
        wx.GetApp().get_project_object().reload_object_list()
    else:
        get_available_objects(True)
    exec('import scenes.' + modulename + ' as reload_module')
    if _DEBUG: print "test_scene_code 2"
    reload(reload_module) #@UndefinedVariable
    if _DEBUG: print "test_scene_code 3"
    exec('from scenes.'+modulename+' import '+scenename+' as scene')
    if _DEBUG: print "test_scene_code 4"
    try:
        if _DEBUG: print "test_scene_code 5"        
        test = scene() #@UndefinedVariable
        if _DEBUG: print "test_scene_code 5.1"
        time.sleep(0.05)
        test.test_scene = True
        if _DEBUG: print "test_scene_code 5.11"        
        test.enter()
        if _DEBUG: print "test_scene_code 5.12"        
        time.sleep(0.05)
        if _DEBUG: print "test_scene_code 5.13"        
        test.exit()
    except:
        # for some reason, if we don't do the following, images get broken
        if _DEBUG: print "test_scene_code 5.2"        
        raise
    else:
        # for some reason, if we don't do the following, images get broken
        if _DEBUG: print "test_scene_code 5.4"        
    finally:
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
    pp_code = """# This file adds pig and pug to the search path
    
try:
    import sys
    sys.path.append('""" + os.path.split(pug.__path__[0])[0]+"""')
except:
    pass
try:
    import os.path
    path = os.path.split(os.path.split(__file__)[0])[0]
    sys.path.append(path)    
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
        wx.CallAfter( PigDirector.quit, False)
    python_process(project_editor, no_record=True)
    return True


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

def wait_for_state(state):
    "wait_for_state(state): Set scene state then wait until Opioid is ready"
    scene = PigDirector.scene
    oldstate = scene.state
    print "wfs 1",
    scene.state = state
    time.sleep(0.05)
    timer = 0
    print "wfs 2",
    while not (scene.state == state or scene.state.__class__ == state) and \
            getattr(oldstate, 'exitted', True):
        print "wfs 3",        
        if _DEBUG: print "   Waiting for state: ",state
        time.sleep(0.05)         
        timer += 1
        if timer > 50:
            raise ValueError("Pug unable to set scene state") 
                # get next spawn_interval
    print "Wfs 4"
    time.sleep(0.05)
    if _DEBUG: print "   State set"

def wait_for_exit_scene():  
    PigDirector.scene.exit()
    timer = 0
    while not PigDirector.scene.exitted:
        time.sleep(0.05) # give Opioid time to stop
        timer += 1
        if timer > 50:
            raise ValueError("Pug unable to exit scene")
    time.sleep(0.05)         
    
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
    from pig.PigScene import PigScene
    dummyDict = exporter.dummyDict
    dummyKeys = dummyDict.keys()
    for cls in dummyKeys:
        if issubclass(cls, Node):
            dummyDict[cls].delete()
        if issubclass(cls, PigScene):
            dummyDict[cls].exit()
    # wait for Opioid to catch up
    time.sleep(0.25)
