"""This file contains the OpioidInterface that serves as the root project object
for editing Opioid2D PUG projects."""

import os
import imp
import sys
import time

import wx

import Opioid2D
from Opioid2D.public.Node import Node

import pug
from pug_opioid.PugScene import PugScene
from pug_opioid.PugSprite import PugSprite
from pug_opioid.SelectionFrame import SelectionFrame
from pug_opioid.util import get_available_scenes, get_available_objects,\
                            get_project_path, set_project_path, \
                            close_scene_windows                          

class OpioidInterface(pug.ProjectInterface):
    _pugTemplateClass = 'OpioidInterface'
    _scene = ''
    def __init__(self, rootfile, scene = PugScene):
        filepath = os.path.join(os.getcwd(),rootfile)
        projectPath = os.path.dirname(os.path.realpath(filepath))
        set_project_path( projectPath)

        path, self.projectName = os.path.split(projectPath)
        title = ''.join([self.projectName,' - Opioid2D Project'])

        self.create_scene_dict()   
        self.create_object_dict()        
        
        self.Director = Opioid2D.Director   
        
        pug.ProjectInterface.__init__(self)
        import thread
        Opioid2D.Display.init((800, 600), title='Scene')
        thread.start_new_thread(Opioid2D.Director.Run, (scene,))
        app = pug.App(projectObject=self, 
                      projectFolder=projectPath,
                      projectObjectName=title)
#        thread.start_new_thread(app.start_project,(), 
#                                    {'projectObject':self,
#                                        'projectFolder':projectPath, 
#                                        'projectObjectName':title})
        #Opioid2D.Director.run(PugScene)               
    def _post_init(self):
        self.sceneclass = self.Director.scene.__class__

    def set_sceneclass(self, value):
        """set_sceneclass(value): set the current scene class in the Director

value can be either an actual scene class, or the name of a scene class        
"""
        if value == str(value) and self.sceneDict.has_key(value):
            value = self.sceneDict[value]
        oldscene = Opioid2D.Director.scene
        oldscene_class = Opioid2D.Director.scene.__class__            
        if oldscene_class != value:
            close_scene_windows(oldscene)
            Opioid2D.Director.scene = value
            # wait for completion
            starttime = time.time()
            while Opioid2D.Director.scene.__class__ != value:
                if time.time() - starttime > 5:
                    dlg = wx.MessageDialog(None,''.join([value.__name__,
                     ' has taken over 5 seconds to load. \nContinue waiting?']),
                     'Scene Load Time',wx.YES_NO)
                    if dlg.ShowModal() == wx.ID_NO:
                        break
                    else:
                        starttime = time.time()
                time.sleep(0.05)
    def get_sceneclass(self):
        try:
            scene = Opioid2D.Director.scene.__class__
        except:
            scene = None
        return scene
    sceneclass = property(get_sceneclass, set_sceneclass, 
                     doc="Pick an Opioid2D scene class to edit")
    
    def get_scene(self):
        try:
            return Opioid2D.Director.scene
        except:
            return None
    scene = property(get_scene, doc="The scene object currently being editted")
    
    def revert_scene(self):
        """Revert scene to original state"""
        close_scene_windows()
        sceneclass = Opioid2D.Director.scene = Opioid2D.Director.scene.__class__
    
    def create_scene_dict(self):
        """Reload all scenes from disk"""
        self.sceneDict = {}
        scenelist = get_available_scenes( True)
        for scene in scenelist:        
            self.sceneDict[scene.__name__] = scene
            
    def save_scene(self):
        """Save the current scene as a class in the scenes folder"""
        name = Opioid2D.Director.scene.gname
        if not name:
            name = self.get_sceneclass().__name__
        if name == 'PugScene' or name == 'Scene':
            name = 'MyScene'
        dlg = wx.TextEntryDialog( None, "Enter the scene's class/file name", 
                                  "Enter name", name)
        sceneName = ''
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
        dlg.Destroy()
        pug.code_export( self.scene, path, True, {'name':sceneName})
        scenelist = get_available_scenes(True)
        loadscene = None
        for scene in scenelist:
            if scene.__name__ == sceneName:
                loadscene = scene
#        Opioid2D.Director.scene.__class__ = loadscene
        if loadscene:
            self.sceneclass = loadscene

    # object adding functionality
    addObjectClass = PugSprite            
    def create_object_dict(self):
        """Reload all saved object classes from disk"""
        self.objectDict = {}
        objectlist = get_available_objects( True)
        addName = self.addObjectClass.__name__
        for object in objectlist:
            if object.__name__ == addName:
                self.addObjectClass = object
            self.objectDict[object.__name__] = object            
    def add_object(self, nodeclass=None):
        """add_object( nodeclass=None)
        
Add an object to the scene
"""
        if nodeclass is None:
            objectclass = self.addObjectClass
        if not issubclass(objectclass, Node):
            raise TypeError("add_object(): arg 1 must be a subclass of Node")
        node = objectclass()
        
    def _on_pug_quit(self):
        Opioid2D.Director.quit()

quitting = False
def project_quit(*args, **kwargs):
    """project_quit(*args, **kwargs)
    
This is meant to have the app confirm project closure. Doesn't work right now.
"""
    app._evt_project_frame_close() # just let it crash
    return 
#################################################
    global quitting
    app = wx.GetApp()
    if not quitting and not app.quitting:
        app._evt_project_frame_close()
    quitting = True
Opioid2D.Director.quit = project_quit                    
                    
def _scene_list_generator():
    """_scene_list_generator( includeNewScene=True)-> list of scenes + 'New'
    
Return a list of scene classes available in the scenes folder. Append to that
list a tuple ("New Scene", PugScene) for use in the sceneclass dropdown"""
    list = get_available_scenes()
    list.insert(0,("New Scene", PugScene))
    return list
            
def _object_list_generator():
    """_object_list_generator( includeNewScene=True)-> list of scenes + 'New'
    
Return a list of node classes available in the objects folder. Append to that
list a tuple ("Sprite", PugSprite) for use in the add object dropdown"""
    list = get_available_objects()
    list.insert(0,("New Sprite", PugSprite))
    return list                
        
_interfaceTemplate = {
    'size':(350,350),
    'name':'Basic',
    'attributes':[ 
        [' Current Scene', pug.Label],
        ['sceneclass', pug.Dropdown, {'label':'   Select Scene',
                                 'list_generator':_scene_list_generator}],
        ['scene', None,  {'label':'   View Scene'}],
        ['save_scene', None,  {'label':'   Save Scene'}],
        ['revert_scene', None,  {'label':'   Revert Scene'}],
        ['create_scene_dict', None,  {'label':'   Reload Scenes'}],
        ['', pug.Label, {'label':' Add Object'}],
        ['addObjectClass', pug.Dropdown, 
                             {'list_generator':_object_list_generator,
              'label':'   Object to add',
              'tooltip':'Select an object type for the add button below'}],
        ['add_object', None, {'tooltip':\
              'Add an object to the current scene.\nSelect object type above.',
                              'use_defaults':True,
                              'label':'   Add Object'}],
        ['create_object_dict', None, {'label':'   Reload Objects'}],
        
        [' Utilities', pug.Label],
        ['Director'],
    ]
}
pug.add_template('OpioidInterface', _interfaceTemplate, True)