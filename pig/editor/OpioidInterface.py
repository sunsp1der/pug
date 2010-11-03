"""This file contains the OpioidInterface that serves as the root project object
for editing Opioid2D PUG projects."""

import os
import shutil
import time
import thread
import sys
import traceback

import wx
from wx.lib.dialogs import ScrolledMessageDialog
wx=wx

import Opioid2D
from Opioid2D.public.Node import Node

import pug
import pug.component
from pug.util import kill_subprocesses, get_package_classes, start_file
from pug.component.pugview import _dataPugview, _dataMethodPugview
from pug.syswx.util import show_exception_dialog, cache_default_view
from pug.syswx.component_browser import ComponentBrowseFrame
from pug.syswx.pugmdi import PugMDI
from pug.syswx.drag_drop import FileDropTarget

from pig import PigScene, PigSprite, PigDirector, PauseState
from pig.util import fix_project_path, set_project_path, save_project_settings,\
        entered_scene, start_scene, get_gamedata, create_gamedata, \
        get_display_center, skip_deprecated_warnings, set_opioid_window_position
from pig.editor.StartScene import StartScene
from pig.editor import hacks, EditorState
from pig.editor.GraphicsManager import graphicsManager
from pig.editor.util import get_image_path, get_project_path, test_scene_code,\
        edit_project_file, on_drop_files, close_scene_windows, wait_for_state,\
        get_available_objects, get_available_scenes, create_new_project,\
        open_project, save_scene_as, wait_for_exit_scene, python_process
 
_DEBUG = False

class OpioidInterface(pug.ProjectInterface):
    """OpioidInterface( rootfile, scene=PigScene)
    
rootfile: a file in the root folder of the project, usually the main python 
    module    
scene: the scene to load initially
"""
    _pug_pugview_class = 'OpioidInterface'
    _scene = ''
    component_browser = None
    _use_working_scene = True
    _new_scene = True
    _initialized = False
    _quitting = False
    def __init__(self, rootfile, scene=PigScene):
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
        self.Director = PigDirector   
        self.Director.editorMode = True
                
        thread.start_new_thread(start_opioid, 
                                          (self.pug_settings.rect_opioid_window,
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

    def create_default_project_settings(self, settingsObj=None):
        """create_default_project_settings(settingsObj=None)->setting data class

settingsObj: an object similar to the one below... if it is missing any default
    attributes, they will be replaced here.
"""    
        # DEFAULT GAME SETTINGS
        class project_settings():
            title = os.path.split(get_project_path())[1]
            initial_scene = '__Working__'
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
            initial_scene = "__Working__"
            Rect_Pig_Editor = (470, 150, 550, 600)
            rect_opioid_window = (0, 0, 800 , 600)
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
            pug.code_export( self.pug_settings, "_pug_settings.py", True, 
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
                project_settings.initial_scene = self.pug_settings.initial_scene
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
          
    __cached=[0, 0, 0]      
    def _post_init(self):
        app = wx.GetApp()
        app.set_pug_settings( self.pug_settings)
        code_exceptions = {}
        initial_scene = getattr(self.pug_settings, 'initial_scene', 'PigScene')
        self.reload_components( doReload=True)
        self.reload_scene_list( doReload=True)
        # initial scene
        if initial_scene != 'PigScene' and initial_scene in self.sceneDict:
            # test initial scene                
            try:
                if self.sceneDict[initial_scene].__module__ == \
                                                        'scenes.__Working__':
                    test_scene_code( initial_scene, '__Working__')
                else:
                    test_scene_code( initial_scene)
            except:
                key = '*Error loading initial scene ('+initial_scene+')'                
                code_exceptions[key] = sys.exc_info()
                self.sceneclass = PigScene
            else:
                self.sceneclass = initial_scene
                if self.sceneclass.__module__ == 'scenes.__Working__':
                    self._new_scene = False
        else:
            self.sceneclass = PigScene
        
        # default menus
        if not self.__cached[2]:
            app.add_global_menu("Pig",
                [["New Project", self.new_project, 
                        "Create a new Pig project"],
                 ["Open Project", self.open_project,
                        "Open a Pig project"],
                 ["*DIVIDER*"],
                 ["New Scene\tCtrl+N", [self.set_scene, ("PigScene", True), {}],
                        "Create a new PigScene"],
                 ["Save Working Scene\tCtrl+S", self.save_using_working_scene,
                        "Save current scene in scenes/__Working__.py"],
                 ["Commit Scene\tShift+Ctrl+S", self.commit_scene,
                        "Commit current scene into scenes folder"],
                 ["New Object\tShift+Ctrl+N", self.add_object,
                        "Add the currently selected add object to the scene"],
                 ["*DIVIDER*"],
#                 ["Selection Tab", self.open_selection_frame, 
#                        "Open a new tab to view selected objects"],
                 ["Edit Python File\tCtrl+E", edit_project_file,
                        "Edit a python code file."],
                 ["Open Project Folder\tCtrl+O", self.open_project_folder,
                        "Open the current project's root folder"],
                 ["Raise Windows\tCtrl+W", app.raise_all_frames,
                        "Raise all PUG Windows to top"],
                 ["Quit\tCtrl+Q", self.quit]])
            self.__cached[2]=True
        # open MDI frame
        if not app.get_project_frame():
            frame = PugMDI(
                        [[self, {'objectpath':"Project",'name':"ProjectFrame"}],
                        [self.scene, {'title':"Scene",'name':"SceneFrame"}],
                        ['selection', {'name':"Selection"}],
                        ],
                    title=''.join(["P.I.G. Editor - ", self.project_name]),
                    name="Pig Editor")
            app.set_project_frame(frame)
        else:
            frame = app.get_project_frame()
        target = FileDropTarget(self)
        frame.SetDropTarget( target)
        frame.GetNotebook().Split(2, wx.LEFT)
        size = frame.GetSize()
        frame.GetNotebook().GetPage(1).SetSize([size[0]/2,size[1]])
        # cache a sprite view for speed on first selection
        if not self.__cached[0]:
            dummy = PigSprite( register=False)
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
        self.reload_project_files( errors=code_exceptions)
   
    def on_drop_files(self, x, y, filenames):
        # pass to util function
        return on_drop_files( x, y, filenames)
            
    def open_project_folder(self):
        return start_file(get_project_path())
            
    def quit(self, query=True):
        """quit( query=True)
        
query: if True, query the user about saving the current scene first
"""        
        print "OpioidInterface.quit: self.Director.quit"
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
                if value == "PigScene":
                    value = PigScene
        else:
            if _DEBUG: print "set_scene 3"
            if value not in self.sceneDict.values():
                self.reload_scene_list()
                value = self.sceneDict.get(value.__name__, value)
        oldscene = self.Director.scene
        if oldscene.__class__ != value or forceReload:
            if _DEBUG: print "OpioidInterface.set_scene", value
#            try:
#                print "set_scene 3.5"
#                if value.__module__ == 'scenes.__Working__':
#                    test_scene_code(value.__name__, '__Working__')
#                else:
#                    test_scene_code(value.__name__)
#            except:
#                print "set_scene 3.6"
#                self.set_scene( PigScene, forceReload=True)
#                wx.GetApp().get_project_frame().refresh()
#                show_exception_dialog( prefix='Unable to set scene: ')
#                return
            self._new_scene = True
            self.set_selection([])
            close_scene_windows(oldscene)
            self.stop_scene(False)
            # wait for completion
            starttime = time.time()
            self.Director.scene = value
            time.sleep(0.1)
            if _DEBUG: print "set_scene 4"            
            while self.Director.scene.__class__ != value or \
                    self.Director.scene is oldscene:
                if time.time() - starttime > 30:
                    dlg = wx.MessageDialog(None,''.join([value.__name__,
                ' has taken over 30 seconds to load. \nContinue waiting?']),
                'Scene Load Time',wx.YES_NO)
                    if dlg.ShowModal() == wx.ID_NO:
                        return
                    else:
                        starttime = time.time()
                time.sleep(0.05)
            time.sleep(0.05)
            if _DEBUG: print "set_scene 5"
            wait_for_state(EditorState)
            if _DEBUG: print "set_scene 6"
            entered_scene()
            wx.GetApp().refresh()
            
    def _set_sceneclass( self, val):
        self.stop_scene()
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
    
    def reload_scene(self):
        """Reload scene from version on disk"""
        if _DEBUG: print 'reload_scene 1'
        if self.Director.scene.__class__ == PigScene:
            self.set_scene("PigScene")
            return
        if _DEBUG: print 'reload_scene 2'
        scenename = self.scene.__class__.__name__
        try:
            if _DEBUG: print 'reload_scene 3'
            test_scene_code(scenename)
        except:
            if _DEBUG: print 'reload_scene 3.2'            
            show_exception_dialog(prefix='Unable to reload scene: ')
        else:
            if _DEBUG: print 'reload_scene 3.4'            
            self.revert_working_scene()
            self.set_scene(scenename, True)
        
    def revert_working_scene(self):
        """copy scene file into __Working__ scene file"""
        scenename = self.scene.__class__.__name__ 
        original_file = os.path.join('scenes', 
                                     ''.join([scenename, '.py']))
        working_file = os.path.join('scenes', '__Working__.py')
        shutil.copy( original_file, working_file)
    
    def reload_scene_list(self, doReload=True, errors=None):
        """Load changes made to scene class files"""
        self.sceneDict = get_available_scenes( doReload, self.use_working_scene,
                                               errors=errors)

    def reload_object_list(self, doReload=True, errors=None):
        """Load changes made to object class files"""
        addName = self.addObjectClass.__name__
        objectDict = get_available_objects( doReload, errors=errors)
        self.addObjectClass = objectDict.get(addName, PigSprite)
        
    def reload_components(self, doReload=True, errors=None):
        """Load changes made to project components"""
        get_package_classes('components', 
                            pug.component.Component, #@UndefinedVariable
                            doReload=doReload, errors=errors)
        
    def reload_project_files(self, doReload=True, errors=None,
                             show_dialog=True):
        """reload_project_files(doReload=True, errors=None, show_dialog=True)

doReload: force reload of all files
errors: dict of errors. Will be filled with file errors. Errors can be provided
    in one of two forms... 1)module: sys.exc_info() or 2)*header: sys.exc_info()
show_dialog: show a dialog displaying all file errors found
"""
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
            err = ScrolledMessageDialog( wx.GetApp().get_project_frame(),
                                         msg, 'Project File Errors', 
                                         size=(640, 320), 
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER) 
            err.ShowModal()
            err.Destroy()            
 
                    
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
        
    def open_selection_frame(self):
        """Open a pug window for selected object"""
        wx.GetApp().get_project_frame().open_selection_child()
        
    def nudge(self, vector):
        for obj in wx.GetApp().selectedObjectDict:
            if hasattr(obj, 'position'):
                obj.position = (obj.position[0] + vector[0], 
                                obj.position[1] + vector[1])  
 
    def _on_pug_quit(self):
        if getattr(self.project_settings,'save_settings_on_quit',True):
#            if '__Working__' in self.Director.scene.__module__:
#                self.project_settings.initial_scene = '__Working__'
#            else:
            self.project_settings.initial_scene = self.scene.__class__.__name__
            try:
                save_project_settings( self.project_settings)
            except:
                show_exception_dialog()
        if getattr(self.pug_settings,'save_settings_on_quit',True):
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
        self._quitting = True 
        dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                       "Save Working Scene Before Quit?",
                       'Project Frame Closed', 
            wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_QUESTION)
        try:
            wx.GetApp().projectFrame.RequestUserAttention()
        except:
            pass
        answer = dlg.ShowModal() 
        if answer == wx.ID_YES:
            self.stop_scene()
            saved = self.save_using_working_scene()
            if not saved:
                dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                       "The scene failed to save properly.\nShut down anyway?",
                       'Save Failed', 
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                continue_shutdown = dlg.ShowModal()
                if continue_shutdown == wx.ID_NO:
                    self._quitting = False
                    return False
        elif answer == wx.ID_CANCEL:
            self._quitting = False
            return False
        return True
    
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
            
    def _get_use_working_scene(self): 
        return self._use_working_scene
    def _set_use_working_scene(self, value):
        if self._use_working_scene == value:
            return
        self._use_working_scene = value
        self.reload_scene_list(True)
        if value:
            for cls in self.sceneDict.values():
                if '__Working__' in cls.__module__:
                    self.set_scene(cls)
                    break
        else:
            if '__Working__' in self.Director.scene.__module__:
                self.reload_scene()
    use_working_scene = property(_get_use_working_scene, 
                                   _set_use_working_scene, 
                             doc="Using a working copy of the scene")
    def save_using_working_scene(self, event=None):
        """Save the current scene as scenes/__Working__.py"""
        self.use_working_scene = True
        scenename = self.scene.__class__.__name__ 
        if _DEBUG: print "s0"
        if scenename in ['PigScene', 'Scene']:
            # this is a new scene that hasn't been saved before
            saved = save_scene_as()
            if _DEBUG: print "s1",
            if not saved:
                if _DEBUG: print "s2",
                return False
            else:
                if _DEBUG: print "s3",
                self.sceneDict[self.Director.scene.__class__.__name__] = \
                                                self.Director.scene.__class__
                if _DEBUG: print "s4",
            # we want to save as the new scene name AND as working scene...
        if self._new_scene:
            # hack in user code from original file
            if _DEBUG: print "s5",
            self.revert_working_scene()
            self._new_scene = False
            if _DEBUG: print "s6",            
        # save the scene in __working__
        if _DEBUG: print "s7",    
        saved = save_scene_as( self.scene.__class__.__name__, '__Working__.py')
        if _DEBUG: print "s8",
        if not saved:
            if _DEBUG: print "s9",
            return False
        else:
            if _DEBUG: print "s10",
            self.sceneDict[self.Director.scene.__class__.__name__] = \
                                                self.Director.scene.__class__
            if _DEBUG: print "s11",
        wx.GetApp().refresh()
        if _DEBUG: print "s12",
        return True            
        
    def commit_scene(self):
        self.stop_scene()
        filename = save_scene_as()
        if _DEBUG: print "s13",
        if filename:
            if _DEBUG: print "s14",
            self.revert_working_scene()
            if _DEBUG: print "s15",
            self.sceneDict[self.Director.scene.__class__.__name__] = \
                                                self.Director.scene.__class__
            if _DEBUG: print "s16",
        return filename

    def rewind_scene(self):
        """rewind_scene(): reset the scene and play it again"""
        if not self.Director.game_started:
            return
        gamedata = get_gamedata()
        scene = gamedata.start_sceneclass
        create_gamedata()
        self.Director.game_started = False
        self.Director.switch_scene_to(scene)

    def play_scene( self, doSave=True):
        """play_scene(doSave=True)
        
start the current scene playing. 
doSave: save working copy first
"""
        if _DEBUG: print "play_scene"
        if self.Director.game_started:
            # don't do anything if game started
            return False
        if doSave:
            saved = self.save_using_working_scene()
            if not saved:
                dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                       "The scene failed to save properly.\nPlay anyway?",
                       'Save Failed', 
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                continue_shutdown = dlg.ShowModal()
                if continue_shutdown == wx.ID_NO:
                    return False  
            else:
                self.set_scene(self.scene.__class__.__name__, True)
        #self.reload_scene()
        pug.set_default_pugview("Component", _dataMethodPugview)
#        app = wx.GetApp()
#        app.set_selection([])
        start_scene()
        return True
    
    def pause_scene(self):
        """pause_scene(): pause the current scene"""
        if self.Director.game_started:
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
        if not doRevert:
            self.do_stop_scene(doRevert)
        else:
            try:
                button_info_dict['agui'].button_press(button='stop')
            except:
                self.do_stop_scene(doRevert)
        
    def do_stop_scene(self, doRevert=True):      
        if _DEBUG: print "stop_scene 1"
        if _DEBUG: print "stop_scene"
        if not getattr(self.Director, "game_started", False):
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
            self.set_scene(scene.__name__, True)
        if _DEBUG: print "stop_scene 7"            
        
    def execute_scene( self, doSave=True):
        """execute_scene()
        
Run the scene being editted in a new process.
"""
        try:
            if doSave and not self.Director.game_started:
                saved = self.save_using_working_scene()
                if not saved:
                    dlg = wx.MessageDialog( wx.GetApp().projectFrame,
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
        
    def _on_set_busy_state(self, on):
        """_on_set_busy_state(on)
        
Callback from pugApp notifying that app is becoming busy or unbusy.
"""
        if isinstance(self.scene.state, EditorState):
            self.scene.state._on_set_busy_state(on)
            
    def add_object(self, nodeclass=None):
        """add_object( nodeclass=None)
        
If nodeclass is None, addObjectClass will be used.
"""
        # delay hack necessary to solve Opioid2D thread problem with images
        if nodeclass is None:
            nodeclass = self.addObjectClass
        (Opioid2D.Delay(0) + Opioid2D.CallFunc(self.do_add_object, 
                                               nodeclass)).do() 
        
    addObjectClass = PigSprite
    def do_add_object(self, objectclass):
        """do_add_object( objectclass)
        
Add an object of class objectclass to the scene. Because of timing issues with 
Opioid2D, it is safer to call this via add_object. 
"""
        try:
            if not issubclass(objectclass, Node):
                if _DEBUG: print objectclass, Node
                raise TypeError("add_object(): arg 1 must be a subclass of Node")
        except:
            if _DEBUG: print objectclass, Node
            raise
        node = objectclass()
        if objectclass == PigSprite and type(self.scene.state) == EditorState:
            # set a default image for basic sprite
            try:
                node.set_image("art\\pug.png")
            except:
                pass
            node.position = get_display_center()
            node.layer = "Background"
        #let components do fanciness, then continue
        (Opioid2D.Delay(0) + Opioid2D.CallFunc(self.do_add_object2, node)).do()
    
    def do_add_object2(self, node):
        # avoid overlapping sprites exactly
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
                        nodeloc[0] += 10
                        nodeloc[1] += 10
                        okay_position = False
                        break
            node.rect.left = nodeloc[0]
            node.rect.top = nodeloc[1]
        except:
            pass
        # deal with Opioid image idiosyncracies HACK
        if hasattr(node, 'set_image_file') and\
                hasattr(node, 'get_image_file'):
            node.set_image_file( node.get_image_file())
        wx.CallAfter(wx.GetApp().set_selection,[node])
        
    def kill_subprocesses(self):
        kill_subprocesses()
        
    def test(self, test=None):#, range1=0, range2=100):
        #get_all_objects(Component)
        gamedata = get_gamedata()
        gamedata.gameover()
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
               
def start_opioid( rect, title, icon, scene):
    #start up opioid with a little pause for threading
    skip_deprecated_warnings()    
    time.sleep(0.1)
    
    set_opioid_window_position(rect[0:2])
    Opioid2D.Display.init(rect[2:4], 
                          title=title, 
                          icon=icon)
    Opioid2D.Director.game_started = False
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
    except:
        try:
            wx.GetApp().Exit()
        except:
            pass
#        print "start_opioid: gotcha"
        raise
         
def _scene_list_generator():
    """_scene_list_generator( includeNewScene=True)-> list of scenes + 'New'
    
Return a list of scene classes available in the scenes folder. Append to that
list a tuple ("New Scene", PigScene) for use in the sceneclass dropdown"""
    if _DEBUG: print "_scene_list_generator"
    scenedict = get_available_scenes( 
                    useWorking = wx.GetApp().projectObject._use_working_scene)
    scenelist = scenedict.values()
    scenelist.sort()
    scenelist.insert(0,("New Scene", PigScene))
    return scenelist    
        
from pig.editor.agui import ObjectsDropdown      
from pig.editor.agui import ScenesDropdown      

button_info_dict = {}
_interfacePugview = {
    'size':(350,350),
    'name':'Pig Editor',
    'skip_menus':['Export'],    
    'no_source':True,
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
              'prepend_list':[("New Scene", PigScene)],
              'doc':"Pick a scene to edit"}],
        ['commit_scene', None, {
                               'label':"   Commit Scene", 
                               'doc':"Commit current scene to disk",
                               'no_return_popup':True}],
#        ['view_scene', pug.Routine,  {'label':'   View Scene'}],
        ['reload_scene', None, {'label':'   Reload Scene'}],
#        ['use_working_scene', None, {'label':'   Use Working Scene',
#                    'doc':'Uncheck to go back to last committed version'}],
        [' Objects', pug.Label],
        ['addObjectClass', ObjectsDropdown, 
             {'prepend_list':[("New Sprite", PigSprite)],
              'label':'   Object to add',
              'doc':'Select an object type for the add button below'}],
        ['add_object', None, {'doc':\
              'Add an object to the scene.\nSelect object type above.',
                              'use_defaults':True,
                              'label':'   Add Object'}],

        [' Settings', pug.Label],
        ['project_settings'],
        ['pug_settings'],

        [' Utilities', pug.Label],
        ['reload_project_files', None, {'label':'   Reload Files',
                                        'use_defaults':True,
                    'doc':"Reload all scene, object,\nand component files"}],
#        ['reload_scene_list', None, {'label':'   Load Scenes',
#                                     'use_defaults':True}],
#        ['reload_object_list', pug.Routine, {'label':'   Load Objects'}],
#        ['open_selection_frame', None, 
#                {'label':'   View Selection'}],
        ['browse_components', None, 
                {'label':'   Browse Components'}],
#        ['Director'],
#        ['Display'],
        ['test', pug.Routine]
    ]
}
pug.add_pugview('OpioidInterface', _interfacePugview, True)
