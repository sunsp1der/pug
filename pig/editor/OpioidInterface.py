"""This file contains the OpioidInterface that serves as the root project object
for editing Opioid2D PUG projects."""

import os
import shutil
import time
import thread
import subprocess

import wx

import Opioid2D
from Opioid2D.public.Node import Node

import pug
from pug.component.pugview import _dataPugview, _dataMethodPugview
from pug.syswx.util import show_exception_dialog, cache_default_view
from pug.syswx.component_browser import ComponentBrowseFrame
from pug.syswx.pugmdi import PugMDI

from pig import PigScene, PigSprite, Director
from pig.util import get_available_scenes, get_available_objects, \
                            set_project_path, start_scene, \
                            save_game_settings, get_project_path
from pig.editor import EditorState, graphicsManager
from pig.editor.util import close_scene_windows, save_scene_as, \
                                    wait_for_state, \
                                    wait_for_exit_scene, get_image_path
 
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
    def __init__(self, rootfile, scene=PigScene):
        if _DEBUG: print "OpioidInterface.__init__"
        try:
            # for process watching purposes
            import dl
            libc = dl.open('/lib/libc.so.6')
            libc.call('prctl', 15, 'python_pig', 0, 0, 0)
        except:
            # we're probably not in linux
            pass
        
        projectPath = os.path.dirname(os.path.realpath(rootfile))
        set_project_path( projectPath)
        self.project_name = os.path.split(projectPath)[1]

        self.reload_scene_list()        
        self.import_settings()
        if getattr(self.game_settings, 'title'):
            self.project_name = self.game_settings.title 

        self.Display = Opioid2D.Display
        self.Director = Director   
        self.Director.editorMode = True
                
#        pug.ProjectInterface.__init__(self)
#        os.environ['SDL_VIDEO_WINDOW_POS'] = \
#                "%d,%d" % self.pug_settings.rect_opioid_window[0:2]
#        Opioid2D.Display.init(self.pug_settings.rect_opioid_window[2:4], 
#                              title='Pig Scene', 
#                              icon=get_image_path('pug.png'))
#        Opioid2D.Director.game_started = False
#        Opioid2D.Director.playing_in_editor = True
#        thread.start_new_thread(self.Director.run, (PigScene,))

        thread.start_new_thread(start_opioid, 
                                          (self.pug_settings.rect_opioid_window,
                                           'Pig Scene',
                                           get_image_path('pig.png'),
                                           PigScene))
        time.sleep(1)
        
        pug.App(projectObject=self, 
                      projectFolder=projectPath,
                      projectObjectName=self.project_name)
        self.Director.realquit()

    def create_default_game_settings(self, settingsObj=None):
        """create_default_game_settings(settingsObj=None)->setting data class

settingsObj: an object similar to the one below... if it is missing any default
    attributes, they will be replaced here.
"""    
        # DEFAULT GAME SETTINGS
        defaultTitle = os.path.split(get_project_path())[1]
        class game_settings():
            title = defaultTitle
            initial_scene = '__Working__'
            rect_opioid_window = (20, 20, 800, 600)
            fullscreen = False
            save_settings_on_quit = True
            
        if settingsObj:
            for attr, data in game_settings.__dict__.iteritems():
                settingsObj.__dict__.setdefault(attr, data)
            return settingsObj
        else:
            return game_settings
    
    def create_default_pug_settings(self, settingsObj=None):
        """create_default_pug_settings(settingsObj=None)->setting data class

settingsObj: an object similar to the one below... if it is missing any default
    attributes, they will be replaced here.
"""
        # DEFAULT PUG SETTINGS
        class pug_settings():
            initial_scene = "PigScene"
            rect_opioid_window = (0, 0, 800, 600)
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
            from _pug_settings import pug_settings
        except:
            self.pug_settings = self.create_default_pug_settings()
            self.save_pug_settings()
        else:
            self.pug_settings = self.create_default_pug_settings( pug_settings)

        # game settings
        try:
            from _game_settings import game_settings
        except:
            game_settings = self.create_default_game_settings()
            if not game_settings.initial_scene:
                game_settings.initial_scene = self.pug_settings.initial_scene
            try:
                save_game_settings( game_settings)
            except:
                if wx.GetApp():
                    show_exception_dialog()
                else:
                    raise
        else:
            game_settings = self.create_default_game_settings(game_settings)
        self.game_settings = game_settings
          
    cached=[0, 0, 0]      
    def _post_init(self):
        app = wx.GetApp()
        app.set_pug_settings( self.pug_settings)
        # initial scene
        if getattr(self.pug_settings, 'initial_scene'):
            scene = self.pug_settings.initial_scene
            available_scenes = get_available_scenes()
            if scene in available_scenes:
                self.sceneclass = scene
                if available_scenes[scene].__module__ == 'scenes.__Working__':
                    self._new_scene = False
        self.set_scene(self.Director.scene.__class__, True)
        # default menus
        if not self.cached[2]:
            app.add_global_menu("Pig",
                [["New Project", self.new_project, 
                        "Create a new Pig project"],
                 ["Open Project", self.open_project,
                        "Open a Pig project"],
                 ["*DIVIDER*"],
                 ["New Scene\tCtrl+N", [self.set_scene, ("PigScene",), {}],
                        "Create a new PigScene"],
                 ["Save Working Scene\tCtrl+S", self.save_using_working_scene,
                        "Save current scene in scenes/__Working__.py"],
                 ["New Object\tShift+Ctrl+N", self.add_object,
                        "Add the currently selected add object to the scene"],
                 ["*DIVIDER*"],
                 ["Raise Windows\tCtrl+W", app.raise_all_frames,
                        "Raise all PUG Windows to top"],
                 ["Quit\tCtrl+Q", self.quit]])
            self.cached[2]=True
        # open MDI frame
        if not app.get_project_frame():
            frame = PugMDI(
                        [[self, {'objectpath':"Project",'name':"ProjectFrame"}],
                        [self.scene, {'title':"Scene",'name':"SceneFrame",
                                'objectpath':self.scene.__class__.__name__}],
                        ['selection', {'name':"Selection"}],
                        ],
                    title=''.join(["Pig Editor - ", self.project_name]),
                    name="Pig Editor")
            frame.GetNotebook().Split(2, wx.LEFT)
            size = frame.GetSize()
            frame.GetNotebook().GetPage(1).SetSize([size[0]/2,size[1]])
            app.set_project_frame(frame)
        # cache a sprite view for speed on first selection
        if not self.cached[0]:
            dummy = PigSprite( register=False)
            cache_default_view( dummy)
            dummy.delete()
            while dummy in self.Director.scene.nodes:
                time.sleep(0.1)
            self.cached[0] = True       
        self._initialized = True     
            
    def quit(self):
        self.Director.quit()
        
    def view_scene(self):
        """Show scene data in a window"""
        pug.frame(self.scene)
            
    def set_scene(self, value, forceReload = False):
        """set_scene(value): set the current scene class in the Director

value can be either an actual scene class, or the name of a scene class        
"""
        if (forceReload):
            self.reload_object_list()
            self.reload_scene_list()
        if value == str(value):
            if self.sceneDict.has_key(value):
                value = self.sceneDict[value]
            else:
                if value == "PigScene":
                    value = PigScene
        else:
            if value not in self.sceneDict.values():
                value = self.sceneDict.get(value.__name__, value)
        oldscene = self.Director.scene
        if oldscene.__class__ != value or forceReload:
            if _DEBUG: print "Interface.set_scene", value
            self._new_scene = True
            self.set_selection([])
            close_scene_windows(oldscene)
            self.stop_scene(False)
            self.Director.scene = value
            # wait for completion
            starttime = time.time()
            while self.Director.scene.__class__ != value or \
                    self.Director.scene is oldscene:
                if time.time() - starttime > 5:
                    dlg = wx.MessageDialog(None,''.join([value.__name__,
                     ' has taken over 5 seconds to load. \nContinue waiting?']),
                     'Scene Load Time',wx.YES_NO)
                    if dlg.ShowModal() == wx.ID_NO:
                        return
                    else:
                        starttime = time.time()
                time.sleep(0.05)
            wait_for_state(EditorState)
            sceneFrame = wx.FindWindowByName("SceneFrame")
            if sceneFrame:
                sceneFrame.set_object(self.Director.scene, title="Scene")
            wx.GetApp().refresh()
            
    def _get_sceneclass(self):
        try:
            scene = self.Director.scene.__class__
        except:
            scene = None
        return scene
    sceneclass = property(_get_sceneclass, set_scene, 
                     doc="Pick an Opioid2D scene class to edit")
    
    def _get_scene(self):
        try:
            return self.Director.scene
        except:
            return None
    scene = property(_get_scene, doc="The scene object currently being editted")
    
    def reload_scene(self):
        """Reload scene from version on disk"""
        self.revert_working_scene()
        self.set_scene(self.scene.__class__.__name__, True)
        
    def revert_working_scene(self):
        """copy scene file into __Working__ scene file"""
        scenename = self.scene.__class__.__name__ 
        original_file = os.path.join('scenes', 
                                     ''.join([scenename, '.py']))
        working_file = os.path.join('scenes', '__Working__.py')
        shutil.copy( original_file, working_file)

    
    def reload_scene_list(self, doReload=True):
        """Load changes made to scene class files"""
        self.sceneDict = get_available_scenes( doReload, self.use_working_scene)
        
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
        wx.GetApp().open_selection_frame()
        
    def nudge(self, vector):
        for obj in wx.GetApp().selectedObjectDict:
            if hasattr(obj, 'position'):
                obj.position = (obj.position[0] + vector[0], 
                                obj.position[1] + vector[1])  
 
    def _on_pug_quit(self):
        if getattr(self.game_settings,'save_settings_on_quit',True):
            if '__Working__' in self.Director.scene.__module__:
                self.game_settings.initial_scene = '__Working__'
            else:
                self.game_settings.initial_scene = self.scene.__class__.__name__
            try:
                save_game_settings( self.game_settings)
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
        dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                       "Save Working Scene Before Quit?",
                       'Project Frame Closed', 
            wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_QUESTION)
        wx.GetApp().projectFrame.RequestUserAttention()
        answer = dlg.ShowModal() 
        if answer == wx.ID_YES and not self.Director.game_started:
            saved = self.save_using_working_scene()
            if not saved:
                dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                       "The scene failed to save properly.\nShut down anyway?",
                       'Save Failed', 
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                continue_shutdown = dlg.ShowModal()
                if continue_shutdown == wx.ID_NO:
                    return False
        elif answer == wx.ID_CANCEL:
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
        pass
    
    def open_project(self):
        """Open a pig project"""
        pass

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
        if scenename in ['PigScene', 'Scene']:
            # this is a new scene that hasn't been saved before
            saved = save_scene_as()
            if not saved:
                return False
            # we want to save as the new scene name AND as working scene...
        if self._new_scene:
            # hack in user code from original file
            self.revert_working_scene()
            self._new_scene = False
        # save the scene in __working__    
        saved = save_scene_as( self.scene.__class__.__name__, '__Working__.py')
        if not saved:
            return False
        wx.GetApp().refresh()
        return True            
        
    def commit_scene(self):
        self.stop_scene()
        if save_scene_as():
            self.revert_working_scene()

    def rewind_scene(self):
        """rewind_scene(): reset the scene and play it again"""
        if not self.Director.game_started:
            return
        self.stop_scene()
        self.play_scene( False)
        
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
        #self.reload_scene()
        pug.set_default_pugview("Component", _dataMethodPugview)
#        app = wx.GetApp()
#        app.set_selection([])
        start_scene()
        return True
    
    def stop_scene( self, doRevert=True):
        """stop_scene(doRevert=True)
        
Stop the current scene from playing. if doRevert, Reload original state from 
disk.
"""
        if _DEBUG: print "stop_scene"
        if not self.Director.game_started:
            return
        self.scene.stop()
        wait_for_exit_scene()
        pug.set_default_pugview("Component", _dataPugview)
        if doRevert:
            self.set_scene(self.scene.__class__.__name__, True)
        
    def execute_scene( self, doSave=True):
        """execute_scene()
        
Run the scene being editted in a new process.
"""
        try:
            if doSave:
                saved = self.save_using_working_scene()
                if not saved:
                    dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                          "The scene failed to save properly.\nExecute anyway?",
                          'Save Failed', 
                          wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                    continue_shutdown = dlg.ShowModal()
                    if continue_shutdown == wx.ID_NO:
                        return False                               
            save_game_settings( self.game_settings)
            subprocess.Popen(["python","main.py",self.scene.__class__.__name__])
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
            
    addObjectClass = PigSprite
    def add_object(self, nodeclass=None):
        """add_object( nodeclass=None)
        
Add an object to the scene
"""
        if nodeclass is None:
            objectclass = self.addObjectClass
        if not issubclass(objectclass, Node):
            raise TypeError("add_object(): arg 1 must be a subclass of Node")
        node = objectclass()
        if objectclass == PigSprite and type(self.scene.state) == EditorState:
            # set a default image for basic sprite
            node.set_image("art/pig.png")
            node.position = \
                    Opioid2D.Vector(*Opioid2D.Display.get_view_size()) * 0.5
            node.layer = "Background"
        wx.GetApp().set_selection([node])
        
    def reload_object_list(self):
        """Load changes made to object class files"""
        addName = self.addObjectClass.__name__
        objectDict = get_available_objects( True)
        self.addObjectClass = objectDict.get(addName, PigSprite)
       
def start_opioid( rect, title, icon, scene):
    #start up opioid with a little pause for threading    
    time.sleep(0.1)
    
    if os.name == "nt":
        loc = (rect[0]+3, rect[1]+28)
    else:
        loc = rect[0:2]
    os.environ['SDL_VIDEO_WINDOW_POS'] = \
            "%d,%d" % loc
    Opioid2D.Display.init(rect[2:4], 
                          title=title, 
                          icon=icon)
    Opioid2D.Director.game_started = False
    Opioid2D.Director.playing_in_editor = True    
    Opioid2D.Director.run( scene)       
         
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

_interfacePugview = {
    'size':(350,350),
    'name':'Pig Editor',
    'skip_menus':['Export'],    
    'attributes':[ 
        ['Project', pug.Label, {'font_size':10}],
        ['Controls', pug.PlayButtons, {'execute':'execute_scene', 
                                       'stop':'stop_scene',
                                       'rewind':'rewind_scene',
                                       'play':'play_scene'}],        

        [' Current Scene', pug.Label],
        ['sceneclass', pug.Dropdown, 
             {'label':'   Select Scene',
              'list_generator':_scene_list_generator}],
        ['commit_scene', None, {
                               'label':"   Save Scene", 
                               'doc':"Commit current scene to disk"}],
#        ['view_scene', pug.Routine,  {'label':'   View Scene'}],
        ['reload_scene', None, {'label':'   Reload Scene'}],
        ['use_working_scene', None, {'label':'   Use Working Scene',
                    'doc':'Uncheck to go back to last committed version'}],
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
        ['game_settings'],
        ['pug_settings'],

        [' Utilities', pug.Label],
        ['reload_scene_list', None, {'label':'   Reload Scenes',
                                     'use_defaults':True}],
        ['reload_object_list', pug.Routine, {'label':'   Reload Objects'}],        
#        ['open_selection_frame', None, 
#                {'label':'   View Selection'}],
        ['browse_components', None, 
                {'label':'   Browse Components'}],
#        ['Director'],
#        ['Display'],
#       ['test', pug.Routine, {'routine':gc.collect}]
    ]
}
pug.add_pugview('OpioidInterface', _interfacePugview, True)
