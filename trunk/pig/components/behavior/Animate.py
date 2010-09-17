import os

import Opioid2D
from Opioid2D.public.Node import Node

from pug import Filename, Dropdown
from pug.component import *

class Animate(Component):
    """This object is an animation. Animations are stored in folders containing
numbered graphics files with the same name as the folder. For example: "frame0",
"frame1", and "frame2" in a folder called "frame". Note: if you have 10 or more 
frames, number with zeros, like this: "frame08", "frame09","frame10","frame11"
"""
    #component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    # separate these to make derived components easier to write
    _field_list = [ 
            ['folder',Filename,{'doc':'Folder containing animation files', 
                                'type':'folder', 'subfolder':'art',
                                'allow_delete': True, 'message':
                                'Choose a folder containing animation frames'}],
            ['fps','Frames per second'],
            ['mode',Dropdown,{'doc':'Stop runs through once,\n'+\
                                    'Repeat repeats forward only,\n'+\
                                    'PingPong repeats forward then back',
                                'list':["Stop","Repeat","PingPong"]
                                }],
            ['destroy',
             'Destroy this object when animation completes. Stop mode only.'],
            ]
    #defaults
    _folder = ""
    fps = 15
    mode = "PingPong"
    destroy = False  
    
    frames = None  
    modes = {"Stop":Opioid2D.StopMode, "Repeat":Opioid2D.RepeatMode,
             "PingPong":Opioid2D.PingPongMode}
    action = None
        
    def set_folder(self, folder):
        "Set the animation folder"
        self._folder = folder
        if not getattr(Opioid2D.Director,"start_project",False):
            self.action = (Opioid2D.Delay(0)+ Opioid2D.CallFunc(
                                                self.do_set_folder)).do()
        else:
            self.do_set_folder()
    
    def do_set_folder(self):
        frames = None
        if self.folder:
            try:
                filename = os.path.split(self.folder)[1]
                path = os.path.join(self.folder,filename+"*.*")
                frames = Opioid2D.ResourceManager.get_pattern(path)
            except:
                self._folder = None
                try:
                    if getattr(Opioid2D.Director,"viewing_in_editor"):
                        import wx
                        errorDlg = wx.MessageDialog( 
                                            wx.GetApp().get_project_frame(),
                                            "Unable to load animation",
                                            "Animation Error", wx.OK)
                        errorDlg.ShowModal()
                        errorDlg.Destroy()
                        wx.GetApp().refresh()
                except:
                    frames = None
        if frames:
            self.frames = frames
        else:
            self.frames = None
        if not getattr(Opioid2D.Director,"start_project",False):
            self.show_editor_frame()
    def get_folder(self):
        return self._folder
    folder = property(get_folder, set_folder)
    
    @component_method            
    def on_delete(self):
        "Deconstruct component"
        #hack
        if self.action:
            if self.action._callbacks:
                self.action._callbacks = None
            
    def show_editor_frame(self, imagenum=None):
        if self.owner:
            if self.frames: 
                if imagenum==None:
                    imagenum = len(self.frames)/2
                try:
                    self.owner.image_file = self.frames[imagenum]     
                except:
                    pass
                else:
                    self.owner.image_file = None
                    return
            self.owner.image_file = "art\\pug.png"
    
    @component_method
    def on_added_to_scene(self, scene):
        """Show text when object is added to scene"""
        if self.frames:
            action = Opioid2D.Animate(self.frames, fps=self.fps, 
                                     mode=self.modes[self.mode])
            if self.destroy:
                action += Opioid2D.CallFunc(self.owner.destroy)
            self.owner.do(action)
        
    @component_method
    def on_added_to_editor(self, scene):
        """Show text when object or component is added to editor"""
        self.set_folder( self.folder)    

    def on_removed_from_object(self):
        self.owner.set_image_file("art\\pug.png")

register_component( Animate)
