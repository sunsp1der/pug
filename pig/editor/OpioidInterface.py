"""This file contains the OpioidInterface that serves as the root project object
for editing Opioid2D PUG projects."""

import os
import shutil
import time
import thread
import sys
import traceback
from functools import partial

import wx
from wx.lib.dialogs import ScrolledMessageDialog
wx=wx

import Opioid2D
from Opioid2D.public.Node import Node

#import wm_ext as canvas # canvas window control extensions 
from wm_ext.appwnd import AppWnd as canvas_manager

import pug
import pug.component
from pug.util import kill_subprocesses, get_package_classes, start_file
from pug.component.pugview import _dataPugview, _dataMethodPugview
from pug.syswx.util import show_exception_dialog, cache_default_view
from pug.syswx.component_browser import ComponentBrowseFrame
from pug.syswx.pugmdi import PugMDI
from pug.syswx.drag_drop import FileDropTarget

from pig import hacks, Scene, Sprite, Director, PauseState
from pig.util import fix_project_path, set_project_path, save_project_settings,\
        start_scene, get_gamedata, create_gamedata, \
        get_display_center, skip_deprecated_warnings, set_opioid_window_position
from pig.editor.StartScene import StartScene
from pig.editor import EditorState
from pig.editor.GraphicsManager import graphicsManager
from pig.editor.util import *
 
_DEBUG = False

class OpioidInterface(pug.ProjectInterface):
    """OpioidInterface( rootfile, scene=Scene)
    
rootfile: a file in the root folder of the project, usually the main python 
    module    
scene: the scene to load initially
"""
    _pug_pugview_class = 'OpioidInterface'
    _scene = ''
    component_browser = None
    _use_working_scene = False
    _new_scene = True
    _initialized = False
    _quitting = False
    canvas = None
    overlap_offset = (10,10)
    edit_info = None # store info on scene being editted while playing
    def __init__(self, rootfile, scene=Scene):
        if _DEBUG: print "OpioidInterface.__init__"
        try:
            # for process watching purposes
            import dl #@UnresolvedImport
            libc = dl.open('/lib/libc.so.6')
            libc.call('prctl', 15, 'python_pig', 0, 0, 0)
        except:
            # we're probably not in linux
            pass
        rootfile = fix_project_path(rootfile)
        projectPath = os.path.dirname(os.path.realpath(rootfile))
        set_project_path( projectPath)
        self.project_name = os.path.split(projectPath)[1]

        self.import_settings()
        if getattr(self.project_settings, 'title'):
            self.project_name = self.project_settings.title 

        self.Display = Opioid2D.Display
        self.Director = Director   
        self.Director.editorMode = True
        opioid_rect = self.pug_settings.rect_opioid_window # x, y, w, h
        thread.start_new_thread(self.start_opioid, 
                                          (opioid_rect,
                                           os.path.split(projectPath)[1],
                                           get_image_path('pug.png'),
                                           StartScene))
        
        # wait for scene to load
        while not getattr(self.Director, 'scene', False):
            time.sleep(0.001)

        pug.App(projectObject=self, 
                      projectFolder=get_project_path(),
                      projectObjectName=self.project_name)
        if _DEBUG: print "OpioidInterface done with loop. Director.realquit"
        self.Director.realquit()
        try:
            if _DEBUG: print "OpioidInterface: wx.GetApp().Exit()"
            wx.GetApp().Exit()
            if _DEBUG: print "OpioidInterface: wx.GetApp().Exit() done"
            raise SystemExit
        except:
            pass

    __cached=[0, 0, 0]      
    def _post_init(self):
        app = wx.GetApp()
        app.set_pug_settings( self.pug_settings)
        code_exceptions = {}
        initial_scene = getattr(self.pug_settings, 'initial_scene', 'Scene')
        self.reload_components( doReload=True)
        self.reload_scene_list( doReload=True)
        # initial scene
        if initial_scene != 'Scene' and initial_scene in self.sceneDict:
            # test initial scene                
            try:
                test_scene_code( initial_scene)
            except:
                key = '*Error loading initial scene ('+initial_scene+')'                
                code_exceptions[key] = sys.exc_info()
                self.set_scene( Scene)
            else:
                self.set_scene( initial_scene)
        else:
            self.set_scene( Scene)
        
        # default menus
        if not self.__cached[2]:
            app.add_global_menu("&File",
                [["New Project", self.new_project, 
                        "Create a new Pig project"],
                 ["Open Project", self.open_project,
                        "Open a Pig project"],
                 ["*DIVIDER*"],
                 ["&New Scene\tCtrl+N", [self.set_scene, ("Scene", True), {}],
                        "Create a new Scene"],
                 ["&Save...\tCtrl+S", save_scene,
                        "Save scene"],
                 ["Save &As...\tCtrl+A", save_scene_as,
                        "Save scene as"],
                 ["New &Object\tShift+Ctrl+N", self.add_object,
                        "Add the currently selected add object to the scene"],
                 ["*DIVIDER*"],
#                 ["Selection Tab", self.open_selection_frame, 
#                        "Open a new tab to view selected objects"],
                 ["Open Code &Editor\tCtrl+E", open_code_editor,
                        "Open python code editor."],
                 ["Browse Project &Folder\tCtrl+F", self.open_project_folder,
                        "Open the project's folder in a browser"],
                 ["Show All &Windows\tCtrl+W", app.raise_all_frames,
                        "Show all open Pug Windows"],
                 ["&Quit\tCtrl+Q", self.quit]])
            app.add_global_menu("&Edit",
                [["Undo\tCtrl+Z", app.history.undo, "Undo last change group"],
                 ["Redo\tCtrl+Y", app.history.redo, "Redo last undo group"],
                 ["Small Undo\tShift+Ctrl+Z", app.history.small_undo,
                        "Undo last individual change"],
                 ["Small Redo\tShift+Ctrl+Y", app.history.small_redo,
                        "Redo last individual undo"],
                 ["*DIVIDER*"],
                 ["Cut\tCtrl+X", self.cut_selected, "Cut selection"],
                 ["Copy\tCtrl+C", self.copy_selected, "Copy selection"],
                 ["Paste\tCtrl+V", self.paste_clipboard, "Paste selection"]])
            self.__cached[2]=True
        # open MDI frame
        if not app.get_project_frame():
            frame = PugMDI(
                        [[self, {'objectpath':"Project",'name':"ProjectFrame"}],
                        [self.scene, {'title':"Scene",'name':"SceneFrame"}],
                        ['selection', {'name':"Selection"}],
                        ],
                    title=''.join(["P.I.G. Editor - ", self.project_name]),
                    name="Pig Editor", show=False)
            app.set_project_frame(frame)
        else:
            frame = app.get_project_frame()
        target = FileDropTarget(self)
        frame.SetDropTarget( target)
        frame.GetNotebook().Split(2, wx.LEFT)
        size = frame.GetSize()
        frame.GetNotebook().GetPage(1).SetSize([size[0]/2,size[1]])
        wx.FindWindowByName("ProjectFrame").Activate()
        frame._on_raise_all_frames = self.raise_canvas
        # attach window manager to opioid window
        opioid_rect = self.pug_settings.rect_opioid_window # x, y, w, h        
        options = dict(pos=tuple(opioid_rect[0:2]), 
                       size=tuple(opioid_rect[2:4]),
                       opengl=True, doublebuff=True, hardware=True)
        canvas_options = canvas_manager.getDefaultOptions()
        canvas_options.update(options)
        self.canvas = canvas_manager( canvas_options)
        self.frame = frame
        # cache a sprite view for speed on first selection
        if not self.__cached[0]:
            dummy = Sprite( register=False)
            cache_default_view( dummy)
            dummy.delete()
            while dummy in self.Director.scene.nodes:
                time.sleep(0.1)
            self.__cached[0] = True       
        self._initialized = True     
        # Import Psyco if available
        try:
            import psyco
            psyco.full()
        except ImportError:
            pass
        
        # create a project file error report at startup
        self.reload_project_files( errors=code_exceptions, save_reload=False)
        # for some reason, canvas needs to be activated before sound plays
        wx.CallLater(111,self.canvas.Activate) 
        wx.CallLater(222,frame.Raise) 
        wx.CallLater(222,frame.Show) 
   
    def create_default_project_settings(self, settingsObj=None):
        """create_default_project_settings(settingsObj=None)->setting data class

settingsObj: an object similar to the one below... if it is missing any default
    attributes, they will be replaced here.
"""    
        # DEFAULT GAME SETTINGS
        class project_settings():
            title = os.path.split(get_project_path())[1]
            initial_scene = '__Editor__' # scene when using main.py
            rect_opioid_window = (25, 25, 800 , 600)
            fullscreen = False
            save_settings_on_quit = True
            
        if settingsObj:
            for attr, data in project_settings.__dict__.iteritems():
                settingsObj.__dict__.setdefault(attr, data)
            return settingsObj
        else:
            return project_settings
    
    def create_default_pug_settings(self, settingsObj=None):
        """create_default_pug_settings(settingsObj=None)->setting data class

settingsObj: an object similar to the one below... if it is missing any default
    attributes, they will be replaced here.
"""
        # DEFAULT PUG SETTINGS
        class pug_settings():
            initial_scene = "Scene" # editor scene
            Rect_Pig_Editor = (400, 150, 624, 535)
            Rect_Pug_Python_Editor = (10, 100, 800, 600)            
            rect_opioid_window = (10, 10, 800 , 600)
            save_settings_on_quit = True

        if settingsObj:
            for attr, data in pug_settings.__dict__.iteritems():
                settingsObj.__dict__.setdefault(attr, data)
            return settingsObj
        else:
            return pug_settings
        
    def save_pug_settings(self):
        if self.scene:
            self.pug_settings.initial_scene = self.sceneclass.__name__
        if wx.GetApp():
            wx.GetApp().create_frame_settings( self.pug_settings)
        try:
            pug.code_exporter( self.pug_settings, "_pug_settings.py", True, 
                     {'name':'pug_settings'})              
        except:
            if wx.GetApp():
                show_exception_dialog()
            else:
                raise
        
    def import_settings(self):
        # pug settings
        try:
            from _pug_settings import pug_settings #@UnresolvedImport
        except:
            self.pug_settings = self.create_default_pug_settings()
            self.save_pug_settings()
        else:
            self.pug_settings = self.create_default_pug_settings( pug_settings)

        # game settings
        try:
            from _project_settings import project_settings #@UnresolvedImport
        except:
            project_settings = self.create_default_project_settings()
            if not project_settings.initial_scene:
                project_settings.initial_scene = '__Editor__'
            try:
                save_project_settings( project_settings)
            except:
                if wx.GetApp():
                    show_exception_dialog()
                else:
                    raise
        else:
            project_settings = self.create_default_project_settings(
                                                            project_settings)
        self.project_settings = project_settings
          
    def raise_canvas( self):
        if self.canvas.IsIconic():
            self.canvas.Restore()
        self.canvas.Activate()

    def on_drop_files(self, x, y, filenames):
        # pass to util function
        return on_drop_files( x, y, filenames)
            
    def open_project_folder(self):
        return start_file(get_project_path())
            
    def quit(self, query=True):
        """quit( query=True)
        
query: if True, query the user about saving the current scene first
"""        
        if _DEBUG: print "OpioidInterface.quit: self.Director.quit"
        self.Director.quit( query=query)
        
    def view_scene(self):
        """Show scene data in a window"""
        pug.frame(self.scene)
            
    def set_scene(self, value, forceReload=False, doTest=False):
        """set_scene(value, forceReload=False): set the current scene 

value: can be either an actual scene class, or the name of a scene class
forceReload: if True, reload all scenes and objects first. 
"""
        if _DEBUG: print "set_scene 1"
        if forceReload is True:
            self.reload_object_list()
            self.reload_scene_list()
        if value == str(value):
            if _DEBUG: print "set_scene 2"
            if self.sceneDict.has_key(value):
                value = self.sceneDict[value]
            else:
                if value == "Scene":
                    value = Scene
        else:
            if _DEBUG: print "set_scene 3"
            if value not in self.sceneDict.values():
                self.reload_scene_list()
                value = self.sceneDict.get(value.__name__, value)
        oldscene = self.Director.scene
#        _DEBUG = True
        if oldscene.__class__ != value or forceReload:
            if _DEBUG: print "OpioidInterface.set_scene", value
            wx.GetApp().history.clear()
            self._new_scene = True
            self.set_selection([])
            winlist = get_scene_windows(oldscene)
            for win in winlist:
                win.Close()
            self.stop_scene(False)
            # wait for completion
            starttime = time.time()
            self.Director.scene = value
            time.sleep(0.1)
            if _DEBUG: print "set_scene 4"            
            while self.Director.scene.__class__ != value or \
                    self.Director.scene is oldscene:
                if time.time() - starttime > 10:
                    dlg = wx.MessageDialog(None,''.join([value.__name__,
                ' has taken over 10 seconds to load. \nContinue waiting?']),
                'Scene Load Time',wx.YES_NO)
                    if dlg.ShowModal() == wx.ID_NO:
                        self.set_scene( oldscene.__class__)
                    else:
                        starttime = time.time()
                time.sleep(0.5)
                if _DEBUG: print "set_scene 5"
            time.sleep(0.05)
            if _DEBUG: print "set_scene 5"
            wait_for_state(EditorState)
            if _DEBUG: print "set_scene 6"
            entered_scene()
            wx.GetApp().refresh()

    def reload_scene(self):
        """Reload scene from version on disk"""
        if _DEBUG: print 'reload_scene 1'
        scene = self
        self.stop_scene()
        while wx.GetApp().busyState == True:
            time.sleep(0.05)
        dlg = wx.MessageDialog( self.frame,
                       "Current state of scene will be lost.\nContinue?",
                       'Confirm Reload', 
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        go_ahead = dlg.ShowModal()
        if go_ahead == wx.ID_NO:
            return False    
        if Director.scene.__class__ == Scene:
            self.set_scene("Scene")
            return True
        if _DEBUG: print 'reload_scene 2'
        scenename = self.scene.__class__.__name__
        try:
            if _DEBUG: print 'reload_scene 3'
            test_scene_code(scenename)
        except:
            if _DEBUG: print 'reload_scene 3.2'            
            show_exception_dialog(prefix='Unable to reload scene: ')
        else:
            if _DEBUG: print 'reload_scene 3.5'    
            self.set_scene(scenename, True)
            if _DEBUG: print 'reload_scene 3.6'   
            return True         
            
    def _set_sceneclass( self, val):
        self.stop_scene()
        if not self.check_save():
            # raising an exception cancels the change in editor
            raise "sceneclass change declined by user"
        self.set_scene(val)            
    def _get_sceneclass(self):
        try:
            scene = self.Director.scene.__class__
        except:
            scene = None
        return scene
    sceneclass = property(_get_sceneclass, _set_sceneclass, 
                     doc="Scene class currently being edited")
    
    def _get_scene(self):
        try:
            return self.Director.scene
        except:
            return None
    scene = property(_get_scene, doc="The scene object currently being editted")
        
    def revert_working_scene(self):
        """copy scene file into __Working__ scene file"""
        scenename = self.scene.__class__.__name__ 
        original_file = os.path.join('scenes', 
                                     ''.join([scenename, '.py']))
        working_file = os.path.join('scenes', '__Working__.py')
        shutil.copy( original_file, working_file)
    
    def reload_scene_list(self, doReload=True, errors=None):
        """Load changes made to scene class files"""
        self.sceneDict = get_available_scenes( doReload, False, errors=errors)

    def reload_object_list(self, doReload=True, errors=None):
        """Load changes made to object class files"""
        addName = self.addObjectClass.__name__
        objectDict = get_available_objects( doReload, errors=errors)
        self.addObjectClass = objectDict.get(addName, Sprite)
        
    def reload_components(self, doReload=True, errors=None):
        """Load changes made to project components"""
        get_package_classes('components', 
                            pug.component.Component, #@UndefinedVariable
                            doReload=doReload, errors=errors)
        
    def reload_project_files(self, doReload=True, errors=None,
                             show_dialog=True, save_reload=True):
        """reload_project_files(doReload=True, errors=None, show_dialog=True, 
                                reload_scene=True)

doReload: force reload of all files
errors: dict of errors. Will be filled with file errors. Errors can be provided
    in one of two forms... 1)module: sys.exc_info() or 2)*header: sys.exc_info()
show_dialog: show a dialog displaying all file errors found
save_reload: if True, save the working file before reloading project files, then
    reload the scene when done
"""
        if save_reload:
            if not self.check_save():
                return
        if errors is None:
            errors = {}
        self.reload_components(doReload=doReload, errors=errors)
        self.reload_object_list(doReload=doReload, errors=errors)
        self.reload_scene_list(doReload=doReload, errors=errors)
        if show_dialog and errors:
            keys = errors.keys()
            top_keys = [] # *'d keys with specific error headers
            mod_keys = [] # standard keys with error module
            for key in keys:
                if key[0]=='*':
                    top_keys.append(key)
                else:
                    mod_keys.append(key)
            keys.sort()
            top_keys.sort()
            msg = 'The following errors were found in the project files:\n\n'
            for header in top_keys:
                info = errors[header]
                header = header[1:]
                msg += header + ':\n\n'
                msg += ''.join(traceback.format_exception(*info))
                msg += '_'*90 + '\n\n'
            for mod in mod_keys:
                msg += 'Error in module ' + mod +':\n\n'
                info = errors[mod]
                msg += ''.join(traceback.format_exception(*info))
                msg += '_'*90 + '\n\n'
            err = ScrolledMessageDialog( self.frame,
                                         msg, 'Project File Errors', 
                                         size=(640, 320), 
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER) 
            err.ShowModal()
            err.Destroy()            
        if save_reload: 
            Opioid2D.ResourceManager.clear_cache()            
            self.set_scene(self.scene.__class__.__name__, True)
                    
    def set_selection(self, selectList):
        """set_selection( selectList)
        
Select the objects in the list. Display their data in the selectFrame and 
highlight them.
"""
        wx.GetApp().set_selection( selectList)
        
    def on_set_selection(self, selectedObjectDict):
        """on_set_selection( selectedObjectDict)
        
Callback from PugApp...
"""
        if self.Director.scene.state and \
                        self.Director.scene.state.__class__ == EditorState:
            graphicsManager.on_set_selection(selectedObjectDict)
#        if selectedObjectDict:
#            wx.FindWindowByName("Selection").Activate()
        
    def open_selection_frame(self):
        """Open a pug window for selected object"""
        self.frame.open_selection_child()
        
    def nudge(self, vector, list=None):
        """nudge(vector,list): Nudge objects by given vector.
        
vector: amount to move objects by
list: a list of objects. If None, pug's list of selected objects will be used.
"""
        if list is None:
            list = wx.GetApp().selectedObjectDict.keys()
        do_fn = partial( self.do_nudge, vector, list)
        undo_fn = partial( self.do_nudge, (vector[0]*-1, vector[1]*-1), list)
        do_fn()
        wx.GetApp().history.add("Nudge selection", undo_fn, do_fn, 
                                ("nudge",list))

    def do_nudge(self, vector, list=None):
        if list is None:
            list = wx.GetApp().selectedObjectDict.keys()
        for obj in list:
            if hasattr(obj, 'position'):
                obj.position = (obj.position[0] + vector[0], 
                                obj.position[1] + vector[1])
                
    def _on_pug_quit(self):
        if getattr(self.project_settings,'save_settings_on_quit',True):
            try:
                save_project_settings( self.project_settings)
            except:
                show_exception_dialog()
        if getattr(self.pug_settings,'save_settings_on_quit',True):
            if os.name == 'nt':
                try:
                    window_pos = self.canvas.GetWindowPosition()
                    if not self.canvas.IsIconic():
                        self.pug_settings.rect_opioid_window = tuple( 
                                            self.canvas.GetWindowPosition() +\
                                            self.canvas.GetWindowSize())
                except:
                    pass
            self.save_pug_settings()
        self.Director.realquit()
        time.sleep(1)   
        
    def _pre_quit_func(self, event=None):     
        """_pre_quit_func( event=None)->True if quit confirmed else False

This function runs when wx is closed.
event: a wx.Event
"""
        if self._quitting:
            return
        self.stop_scene()
        self._quitting = self.check_save()
        return self._quitting      
    
    def browse_components(self):
        """Open up a window showing all available components"""
        if self.component_browser:
            self.component_browser.Raise()
        else:
            self.component_browser = ComponentBrowseFrame()
            self.component_browser.Show()

    def new_project(self):
        """Create a new pig project"""
        project_path = create_new_project()
        if project_path:
            self.open_project( project_path)            
    
    def open_project(self, project_path=None):
        """Open a pig project"""
        try:
            open_project( project_path)
        except:
            show_exception_dialog()
            return
            
    def save_using_working_scene(self, event=None):
        """Save the current scene as scenes/__Working__.py"""
        saved = save_scene_as( self.scene.__class__.__name__, '__Working__.py')
        if not saved:
            return False
        else:
            self.sceneDict['__Working__'] = \
                                        get_available_scenes()['__Working__']
        wx.GetApp().refresh()
        return True            
        
    def check_save( self, title=None, message=None, force=False):
        """check_save( title=None, message=None, force=False)
    
If changes have been made to scene, offer to save. 
Return values: True = continue without saving, False = cancel, filename = 
    continue, saved as filename.
title: title of window. Default = "Save Scene?"
message: message of window. Default = "Changes that have been made to scene will
                                        be lost. Save first?"
force: if True, offer to save whether or not changes have been made 
"""
        if not wx.GetApp().history.has_changes() and not force:
            return True
        if title is None:
            title = "Save Scene?"
        if message is None:
            message = "Changes that have been made to scene will be lost.\n"+\
                        "Save first?"
        dlg = wx.MessageDialog( self.frame, message, title,
            wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_QUESTION)
        try:
            if self.frame.FindFocus().GetTopLevelParent() != self.frame:
                self.frame.Raise()
                self.frame.RequestUserAttention()
        except:
            pass
        answer = dlg.ShowModal() 
        if answer == wx.ID_YES:
            saved = save_scene()
            if not saved:
                dlg = wx.MessageDialog( self.frame,
                       "The scene failed to save properly.\nContinue anyway?",
                       'Save Failed', 
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                go_ahead = dlg.ShowModal()
                if go_ahead == wx.ID_NO:
                    return False
            else:
                return saved
        elif answer == wx.ID_CANCEL:
            return False       
        else:
            return True

    def rewind_scene(self):
        """rewind_scene(): reset the scene and play it again"""
        if not self.Director.project_started:
            return
        gamedata = get_gamedata()
        scene = gamedata.start_sceneclass
        create_gamedata()
        self.Director.project_started = False
        oldscene = self.Director.scene
        self.Director.set_scene(scene)
        while Director.scene == oldscene:
            time.sleep(0.05)
        entered_scene()

    def play_scene( self, doSave=True):
        """play_scene(doSave=True)
        
start the current scene playing. 
doSave: save working copy first
"""
        if _DEBUG: print "play_scene"
        if self.Director.project_started:
            # don't do anything if game started
            return False
        if doSave:
            saved = self.save_using_working_scene()           
            if not saved:
                dlg = wx.MessageDialog( self.frame,
                       "The scene failed to save properly.\nPlay anyway?",
                       'Save Failed', 
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                continue_shutdown = dlg.ShowModal()
                if continue_shutdown == wx.ID_NO:
                    return False  
                else:
                    self.edit_info = None
            else:
                self.play_working_scene()
        else:
            self.edit_info = None
        #self.reload_scene()
        pug.set_default_pugview("Component", _dataMethodPugview)
#        app = wx.GetApp()
#        app.set_selection([])
        (Opioid2D.Delay(0) + Opioid2D.CallFunc(start_scene)).do()
        return True
    
    def play_working_scene(self):
        winlist = get_scene_windows(Director.scene)
        for win in winlist:
            win.Hide()
        app = wx.GetApp()
        self.edit_info = [Director.scene, app.get_selection().keys(),
                          winlist, app.reset_history()]
        self.set_selection([])
        oldscene = Director.scene
        Director.switch_scene = self.sceneDict['__Working__']
        while Director.scene == oldscene:
            time.sleep(0.05)
        entered_scene()
    
    def pause_scene(self):
        """pause_scene(): pause the current scene"""
        if self.Director.project_started:
            if self.Director.paused:
                self.Director.scene.state.unpause()
            else:
                self.Director.scene.set_state(PauseState, 
                                              self.Director.scene.state) 
    
    def stop_scene( self, doRevert=True):
        """stop_scene(doRevert=True)
        
Stop the current scene from playing. if doRevert, Reload original state from 
disk.
"""
        try:
            button_info_dict['agui'].button_press(button='stop')
        except:
            self.do_stop_scene(doRevert)
        
    def do_stop_scene(self, doRevert=True):      
        if _DEBUG: print "stop_scene"
        if not getattr(self.Director, "project_started", False):
            return
        if _DEBUG: print "stop_scene 1.5"
        wait_for_state(None)
        if _DEBUG: print "stop_scene 2"
        self.scene.stop()
        if _DEBUG: print "stop_scene 3"        
        wait_for_exit_scene()
        if _DEBUG: print "stop_scene 4"        
        gamedata = get_gamedata()
        scene = gamedata.start_sceneclass
        create_gamedata()
        if _DEBUG: print "stop_scene 5"
        pug.set_default_pugview("Component", _dataPugview)
        if _DEBUG: print "stop_scene 6", scene.__name__        
        if doRevert:
            if self.edit_info:
                wx.GetApp().set_busy_state( True)
                Director.switch_scene = self.edit_info[0]
                while Director.scene != self.edit_info[0]:
                    time.sleep(0.05)
                self.restore_editor()
                wx.CallAfter( entered_scene)
            else:
                self.set_scene(scene.__name__, True)
                self.edit_info = None
        if _DEBUG: print "stop_scene 7"  
        
    def restore_editor(self):
        for win in self.edit_info[2]:
            win.Show()
        self.set_selection(self.edit_info[1])
        wx.GetApp().restore_history(self.edit_info[3])
        self.edit_info = None     
        wx.GetApp().set_busy_state(False)
        
    def recover_scene(self):
        "Load the last played scene."
        self.set_scene("__Working__")
                  
    def execute_scene( self, doSave=True):
        """execute_scene()
        
Run the scene being editted in a new process.
"""
        try:
            if doSave and not self.Director.project_started:
                saved = self.save_using_working_scene()
                if not saved:
                    dlg = wx.MessageDialog( self.frame,
                          "The scene failed to save properly.\nExecute anyway?",
                          'Save Failed', 
                          wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    continue_shutdown = dlg.ShowModal()
                    if continue_shutdown == wx.ID_NO:
                        return False                               
            save_project_settings( self.project_settings)
            python_process("main.py", "__Working__")
        except:
            show_exception_dialog()
            return False
        return True
        
    def on_set_busy_state(self, on):
        """_on_set_busy_state(on)
        
Callback from pugApp notifying that app is becoming busy or unbusy.
"""
        if isinstance(self.scene.state, EditorState):
            self.scene.state.on_set_busy_state(on)
            
    def add_object(self, nodeclass=None, position=None):
        """add_object( nodeclass=None)
        
If nodeclass is None, addObjectClass will be used.
position: object will be moved to this position
"""
        if wx.GetApp().busyState:
            return
        wx.GetApp().set_busy_state()
        self.adding_object = True
        # delay hack necessary to solve Opioid2D thread problem with images
        if nodeclass is None:
            nodeclass = self.addObjectClass
        (Opioid2D.Delay(0) + Opioid2D.CallFunc(self.do_add_object, 
                                               nodeclass, position)).do()
        wx.CallAfter( self.set_selection, []) 
        
    addObjectClass = Sprite
    def do_add_object(self, objectclass, position=None):
        """do_add_object( objectclass, position)
        
Add an object of class objectclass to the scene. Because of timing issues with 
Opioid2D, it is safer to call this via add_object. 
objectclass: class of object to add
position: move object to this position
"""
        Director.paused = True
        try:
            if not issubclass(objectclass, Node):
                if _DEBUG: print objectclass, Node
                raise TypeError(
                            "add_object(): arg 1 must be a subclass of Node")
        except:
            if _DEBUG: print objectclass, Node
            raise
        node = objectclass()
        if objectclass == Sprite and type(self.scene.state) == EditorState:
            # set a default image for basic sprite
            try:
                node.set_image("art/pug.png")
            except:
                pass
            node.position = get_display_center()
            node.layer = "Background"
        if position is not None:
            node.position = position
        Director.paused = False
        # let components do image alterations, then check for node overlap
        (Opioid2D.Delay(0.1) + Opioid2D.CallFunc(self.avoid_node_overlap, 
                                               node)).do()
    
    def avoid_node_overlap(self, node):
        "avoid_node_overlap(node): avoid overlapping sprites exactly"
        if node.image == None and node.image_file:
            node.set_image( node.image_file)
        okay_position = False
        nodes = self.Director.scene._get_nodes().keys()
        try:
            nodeloc = [node.rect.left, node.rect.top,
                       node.rect.width, node.rect.height]
            while okay_position == False:
                okay_position = True
                for obj in nodes:
                    if obj == node:
                        continue
                    if nodeloc == [obj.rect.left, obj.rect.top, 
                                   obj.rect.width, obj.rect.height]:
                        nodeloc[0] += self.overlap_offset[0]
                        nodeloc[1] += self.overlap_offset[1]
                        okay_position = False
                        break
            node.rect.left = nodeloc[0]
            node.rect.top = nodeloc[1]
        except:
            pass
        do_fn = partial( unhide_nodes, [node])
        undo_fn = partial( hide_nodes, [node])
        wx.CallAfter(self.set_selection,[node])
        wx.CallAfter(wx.GetApp().set_busy_state, False)
        wx.CallAfter(wx.GetApp().history.add,"Add "+node.__class__.__name__,
                                             undo_fn, do_fn)
        
    def kill_subprocesses(self):
        kill_subprocesses()
        
    def _get_source_code(self):
        app = wx.GetApp()
        selected = app.get_selection()
        if selected:                    
            return selected.popitem()[0]._get_source_code()
        else:
            return PigDirector.scene._get_source_code()
        
    def _get_shell_info(self):
        "_get_shell_info()->info for pug's open_shell command"
        scene = PigDirector.scene
        items = {'_Project':self, 
                 '_'+scene.__class__.__name__:scene}
        nodes = scene.nodes
        indexes = {}
        for node in nodes:
            name = node._get_shell_name()
            if name not in indexes:
                indexes[name]=1
            else:
                indexes[name]+=1
                name=name+"_"+str(indexes[name])
            items[name] = node
        items['_gamedata'] = get_gamedata()
        locals = items.copy()
        import pig.actions
        for action in dir(pig.actions):
            if action[0] != "_":
                locals[action]=getattr(pig.actions,action)
        return dict(rootObject=items,rootLabel="Project Data",locals=locals,
                    pug_view_key=self)
                
    def start_opioid( self, rect, title, icon, scene):
        #start up opioid with a little pause for threading
        skip_deprecated_warnings()    
        time.sleep(0.1)
    
        Opioid2D.Display.init(rect[2:4], 
                              title=title, 
                              icon=icon)
        set_opioid_window_position(rect[0:2])
        Opioid2D.Director.project_started = False
        Opioid2D.Director.viewing_in_editor = True
        try:
            Opioid2D.Director.run( scene)
            import pygame
            pygame.quit()
        except ImportError:
            # we're exiting Opioid altogether...
            try:
                wx.GetApp().Exit()
            except:
                pass
    
    def copy_selected(self):
        self.clipboard = {}
        selectedDict = list(wx.GetApp().selectedObjectDict)
        for item in selectedDict:
            if isinstance(item, Opioid2D.public.Node.Node):
                exporter = pug.code_exporter(item)
                code = exporter.code
                obj = exporter.objCode.popitem()[0]
                self.clipboard[obj] = code
                exporter = None
        
    def cut_selected(self):
        self.copy_selected()
        selectedDict = list(wx.GetApp().selectedObjectDict)
        for item in selectedDict:
            if isinstance(item, Opioid2D.public.Node.Node):
                item.delete()

    def paste_clipboard(self):
        for obj, code in self.clipboard.iteritems():
            exec code
            exec "obj = " + obj
            self.set_selection([obj])
            (Opioid2D.Delay(1) + Opioid2D.CallFunc(self.avoid_node_overlap, 
                                               obj)).do()
            
    t = 0
    def test(self):
        print "passed"
            
# test for floating garbage
#        from pug.util import test_referrers
#        import gc
#        if test is None:
#            i = 0
#            for item in gc.garbage:
#                print i, gc.garbage[i]
#                i+=1
#        else:
#            pug.frame(gc.garbage[test])
#            x= test_referrers(gc.garbage[test])
#            if x: 
#                print test_referrers(x)
#                pug.frame(x)
        
from pig.editor.agui import ObjectsDropdown      
from pig.editor.agui import ScenesDropdown      

button_info_dict = {}
_interfacePugview = {
    'size':(350,350),
    'name':'Pig Editor',
    'skip_menus':['Export'],    
    'attributes':[ 
        ['Project', pug.Label, {'font_size':10}],
        ['Controls', pug.PlayButtons, {'execute':'execute_scene', 
                                       'stop':'do_stop_scene',
                                       'pause':'pause_scene',
                                       'rewind':'rewind_scene',
                                       'play':'play_scene',
                                       'doc':'Controls for current scene',
                                       'agui_info_dict': button_info_dict}],
        [' Current Scene', pug.Label],
        ['sceneclass', ScenesDropdown, 
             {'label':'   Scene',
              'sort': False, 'undo': False,
              'prepend_list':[("New Scene", Scene)],
              'doc':"Pick a scene to edit"}],
#        ['view_scene', pug.Routine,  {'label':'   View Scene'}],
        ['reload_scene', None, {'label':'   Reload Scene',
                                'no_return_popup':True}],
#        ['use_working_scene', None, {'label':'   Use Working Scene',
#                    'doc':'Uncheck to go back to last committed version'}],
        [' Objects', pug.Label],
        ['addObjectClass', ObjectsDropdown, 
             {'prepend_list':[("New Sprite", Sprite)],
              'sort':False, 'undo':False,
              'label':'   Object to add',
              'doc':'Select an object type for the add button below'}],
        ['add_object', None, {'doc':\
              'Add an object to the scene. Select object type above. '+\
              'You can also Shift-Ctrl-Click in canvas.',
                              'use_defaults':True,
                              'label':'   Add Object'}],
        ['overlap_offset', None, {
                    'doc':'Offset new sprites that overlap by this much',
                    'label':'   Overlap Offset', 'undo':False}],

        [' Settings', pug.Label],
        ['project_settings'],
        ['pug_settings'],

        [' Utilities', pug.Label],
        ['reload_project_files', None, {'label':'   Reload Files',
                                        'use_defaults':True,
                'doc':"Reload all scene, object, image, and component files"}],
#        ['reload_scene_list', None, {'label':'   Load Scenes',
#                                     'use_defaults':True}],
#        ['reload_object_list', pug.Routine, {'label':'   Load Objects'}],
#        ['open_selection_frame', None, 
#                {'label':'   View Selection'}],
        ['browse_components', None, 
                {'label':'   Browse Components'}],
        ['recover_scene', None, {'label':'   Recover Scene'}],
#        ['canvas', pug.ObjectButtons],
#        ['Director'],
#        ['Display'],
#        ['test', pug.Routine]
    ]
}
pug.add_pugview('OpioidInterface', _interfacePugview, True)
