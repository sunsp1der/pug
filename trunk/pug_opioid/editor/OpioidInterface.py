"""This file contains the OpioidInterface that serves as the root project object
for editing Opioid2D PUG projects."""

import os
import time
import thread
import subprocess
import sys

import wx

import Opioid2D
from Opioid2D.public.Node import Node

import pug
from pug.syswx.util import ShowExceptionDialog
from pug.syswx.component_browser import ComponentBrowseFrame

from pug_opioid import PugScene, PugSprite
from pug_opioid.util import get_available_scenes, get_available_objects, \
                            set_project_path, start_scene, \
                            save_game_settings
from pug_opioid.editor import EditorState, selectionManager
from pug_opioid.editor.util import close_scene_windows, save_scene_as, \
                                    project_quit

class OpioidInterface(pug.ProjectInterface):
    _pug_template_class = 'OpioidInterface'
    _scene = ''
    component_browser = None
    _use_working_scene = True
    def __init__(self, rootfile, scene=PugScene):
        # put this folder on search path so absolute package names will work
        sys.path.insert( 0, os.path.dirname(os.path.dirname(rootfile))) 
        # for process watching purposes
        import dl
        libc = dl.open('/lib/libc.so.6')
        libc.call('prctl', 15, 'python_Pug_Opioid', 0, 0, 0)
        
        projectPath = os.path.dirname(os.path.realpath(rootfile))
        set_project_path( projectPath)
        self.create_scene_dict()
        
        self.import_settings()

        path, self.projectName = os.path.split(projectPath)
        title = ''.join([self.projectName,' - Opioid2D Project'])

        self.Display = Opioid2D.Display
        self.Director = Opioid2D.Director   
        self.Director.editorMode = True

                
        pug.ProjectInterface.__init__(self)
        os.environ['SDL_VIDEO_WINDOW_POS'] = \
                "%d,%d" % self.pug_settings.opioid_window_rect[0:2]
        Opioid2D.Display.init(self.pug_settings.opioid_window_rect[2:4], 
                              title='Pug_Opioid Scene')
        Opioid2D.Director.game_started = False

        thread.start_new_thread(self.Director.run, (scene,))
        app = pug.App(projectObject=self, 
                      projectFolder=projectPath,
                      projectObjectName=title)
        Opioid2D.Director.realquit()

    def create_default_game_settings(self, settingsObj=None):
        """create_default_game_settings(settingsObj=None)->setting data class

settingsObj: an object similar to the one below... if it is missing any default
    attributes, they will be replaced here.
"""    
        # DEFAULT GAME SETTINGS
        class game_settings():
            opioid_window_rect = (20, 20, 800, 600)
            initial_scene = None
            title = 'Pug_Opioid Game'
            save_settings_on_quit = True
            fullscreen = False
            
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
            opioid_window_rect = (0, 0, 800, 600)
            save_settings_on_quit = True
            initial_scene = "PugScene"

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
                ShowExceptionDialog()
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
                    ShowExceptionDialog()
                else:
                    raise
        else:
            game_settings = self.create_default_game_settings(game_settings)
        self.game_settings = game_settings
                
    def _post_init(self):
        wx.GetApp().set_pug_settings( self.pug_settings)
        wx.GetApp().add_global_menu("Pug_Opioid",
                [["Save Working Scene\tCtrl+S", self.save_using_working_scene],
                 ["Show All Windows\tCtrl+W", wx.GetApp().raise_all_frames],
                 ["Quit\tCtrl+Q", project_quit]])
        if self.pug_settings.initial_scene:
            self.sceneclass = self.pug_settings.initial_scene
        
        if not self.scene:
            self.sceneclass = self.Director.scene.__class__
        # open frame to view scene
        self.view_scene()
        # open selection frame
        self.open_selection_frame()
        
    def view_scene(self):
        """Show scene data in a window"""
        pug.frame(self.scene, name="SceneFrame")
            
    def set_scene(self, value, forceReload = False):
        """set_scene(value): set the current scene class in the Director

value can be either an actual scene class, or the name of a scene class        
"""
        if value == str(value):
            if self.sceneDict.has_key(value):
                value = self.sceneDict[value]
            else:
                if value == "PugScene":
                    value = PugScene
        else:
            if value not in self.sceneDict.values():
                value = self.sceneDict.get(value.__name__, value)
        oldscene = self.Director.scene
        if oldscene.__class__ != value or forceReload:
            oldscene.stop()
            sceneFrame = wx.GetApp().get_object_pugframe(oldscene)
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
            if sceneFrame:
                sceneFrame.set_object(self.Director.scene)            
            close_scene_windows(oldscene)
            self.update_selection()
            self.Director.scene.state = EditorState

    def update_selection(self):
        """update_selection(): remove invalid items in selectedRefSet"""
        refSet = wx.GetApp().selectedRefSet
        refList = list(refSet)
        for item in refList:
            if not item():
                refSet.remove(item)
        self.set_selection(refSet)
            
            
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
    
    def revert_scene(self):
        """Revert scene to last saved version"""
        self.set_scene(self.scene.__class__.__name__, True)
    
    def create_scene_dict(self, doReload=True):
        """Create dict of available scene classes in scenes folder"""
        self.sceneDict = {}
        self.sceneDict = get_available_scenes( doReload, self.use_working_scene)
        
    def set_selection(self, selectList):
        """set_selection( selectList)
        
Select the objects in the list. Display their data in the selectFrame and 
highlight them.
"""
        wx.GetApp().set_selection( selectList)
        
    def on_set_selection(self, selectedRefSet):
        """on_set_selection( selectedRefSet)
        
Callback from PugApp...
"""
        selectionManager.on_set_selection(selectedRefSet)
        
    def open_selection_frame(self):
        """Open a pug window for selected object"""
        wx.GetApp().open_selection_frame()
        
    def nudge(self, vector):
        for ref in wx.GetApp().selectedRefSet:
            obj = ref()
            if hasattr(obj, 'position'):
                obj.position = (obj.position[0] + vector[0], 
                                obj.position[1] + vector[1])  
 
    def _on_pug_quit(self):
        if getattr(self.game_settings,'save_settings_on_quit',True):
            self.game_settings.initial_scene = self.scene.__class__.__name__
            try:
                save_game_settings( self.game_settings)
            except:
                ShowExceptionDialog()
        if getattr(self.pug_settings,'save_settings_on_quit',True):
            self.save_pug_settings()
        Opioid2D.Director.realquit()   
        
    def _pre_quit_func(self, event=None):     
        dlg = wx.MessageDialog( wx.GetApp().projectFrame,
                       "Save Working Scene Before Quit?",
                       'Project Frame Closed', 
            wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_QUESTION)
        answer = dlg.ShowModal() 
        if answer == wx.ID_YES:
            self.save_using_working_scene()
        elif answer == wx.ID_CANCEL:
            return False
        return True
    
    def browse_components(self):
        if self.component_browser:
            self.component_browser.Raise()
        else:
            self.component_browser = ComponentBrowseFrame()
            self.component_browser.Show()

    def _get_use_working_scene(self): 
        return self._use_working_scene
    def _set_use_working_scene(self, value):
        if self._use_working_scene == value:
            return
        self._use_working_scene = value
        self.create_scene_dict(True)
        if value:
            for cls in self.sceneDict.values():
                if cls.__module__ == 'scenes.__Working__':
                    self.set_scene(cls)
                    break
        else:
            if self.Director.scene.__module__ == 'scenes.__Working__':
                self.revert_scene()
    use_working_scene = property(_get_use_working_scene, 
                                   _set_use_working_scene, 
                             doc="Using a working copy of the scene")
    def save_using_working_scene(self, event=None):
        """Save the current scene as scenes/__Working__.py"""
        save_scene_as( self.scene.__class__.__name__, '__Working__')
        self.use_working_scene = True

    def rewind_scene(self):
        """rewind_scene(): reset the scene and play it again"""
        if not Opioid2D.Director.game_started:
            return
        self.stop_scene()
        self.play_scene( False)
        
    def play_scene( self, doSave=True):
        """play_scene(doSave=True)
        
start the current scene playing. 
doSave: save working copy first
"""
        if Opioid2D.Director.game_started:
            # don't do anything if game started
            return
        if doSave:
            self.save_using_working_scene()
        #self.revert_scene()
        start_scene()   
    
    def stop_scene( self):
        """stop_scene()
        
Stop the current scene from playing. Reload original state from disk.
"""
        if not Opioid2D.Director.game_started:
            return
        self.scene.stop()
        self.revert_scene()
        
    def execute_scene( self):
        """execute_scene()
        
Run the scene being editted in a new process.
"""
        try:
            save_game_settings( self.game_settings)
        except:
            ShowExceptionDialog()
        subprocess.Popen( ["python","main.py",self.scene.__class__.__name__])
        
    def _on_set_busy_state(self, on):
        """_on_set_busy_state(on)
        
Callback from pugApp notifying that app is becoming busy or unbusy.
"""
        if isinstance(self.scene.state, EditorState):
            self.scene.state._on_set_busy_state(on)
            
    addObjectClass = PugSprite
    def add_object(self, nodeclass=None):
        """add_object( nodeclass=None)
        
Add an object to the scene
"""
        if nodeclass is None:
            objectclass = self.addObjectClass
        if not issubclass(objectclass, Node):
            raise TypeError("add_object(): arg 1 must be a subclass of Node")
        node = objectclass()
        if objectclass == PugSprite and type(self.scene.state) == EditorState:
            # set a default image for basic sprite
            node.image = "art/pug.png"
            if len(self.scene.layers) > 1:
                # skip 'selection' layer
                node.layer = self.scene.layers[-2]
            else:
                node.layer = "Layer 1"
        wx.GetApp().set_selection([node])
        
    def reload_object_list(self):
        """Load changes made to object class files"""
        objectlist = get_available_objects( True)
        try:
            scene = self.scene
        except:
            return
        addName = self.addObjectClass.__name__
        for object in objectlist:
            if object.__name__ == addName:
                self.addObjectClass = object     
                return
        self.addObjectClass = PugSprite             
         
def _scene_list_generator():
    """_scene_list_generator( includeNewScene=True)-> list of scenes + 'New'
    
Return a list of scene classes available in the scenes folder. Append to that
list a tuple ("New Scene", PugScene) for use in the sceneclass dropdown"""
    dict = get_available_scenes( 
                    useWorking = wx.GetApp().projectObject._use_working_scene)
    list = dict.values()
    list.insert(0,("New Scene", PugScene))
    return list               
        
def _object_list_generator():
    """_object_list_generator()-> list of objects + 'New Sprite'
    
Return a list of node classes available in the objects folder. Append to that
list a tuple ("Sprite", PugSprite) for use in the add object dropdown"""
    list = get_available_objects()
    list.insert(0,("New Sprite", PugSprite))
    return list    
                    
_interfaceTemplate = {
    'size':(350,350),
    'name':'Basic',
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
        ['   Save Scene', pug.Routine, {
                               'routine':save_scene_as, 
                               'use_defaults':True,
                               'tooltip':"Commit current scene to disk"}],
        ['view_scene', pug.Routine,  {'label':'   View Scene'}],
        ['revert_scene', None, {'label':'   Revert Scene'}],
        ['use_working_scene', None, {'label':'   Use Working Scene',
                    'tooltip':'Uncheck to go back to last committed version'}],
 
        [' Objects', pug.Label],
        ['addObjectClass', pug.Dropdown, 
             {'list_generator':_object_list_generator,
              'label':'   Object to add',
              'tooltip':'Select an object type for the add button below'}],
        ['add_object', None, {'tooltip':\
              'Add an object to the scene.\nSelect object type above.',
                              'use_defaults':True,
                              'label':'   Add Object'}],                              
        ['reload_object_list', pug.Routine, {'label':'   Reload Objects'}],        

        [' Settings', pug.Label],
        ['game_settings'],
        ['pug_settings'],

        [' Utilities', pug.Label],
        ['create_scene_dict', None, {'label':'   Reload Scenes',
                                     'use_defaults':True}],
        ['open_selection_frame', None, 
                {'label':'   View Selection'}],
        ['browse_components', None, 
                {'label':'   Browse Components'}],
        ['Director'],
        ['Display'],
#        ['test', pug.Routine, {'routine':test}]
    ]
}
pug.add_template('OpioidInterface', _interfaceTemplate, True)