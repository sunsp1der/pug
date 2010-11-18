import os

import Opioid2D
from Opioid2D.public.Node import Node

from pug import Filename, Dropdown
from pug.component import *

class Animate_Folder(Component):
    """This object is an animation. Folder animations are stored as 
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
            ]
    _animate_list = [
            ['fps','Frames per second'],
            ['mode',Dropdown,{'doc':'Stop runs through once,\n'+\
                                    'Repeat repeats forward only,\n'+\
                                    'PingPong repeats forward then back',
                                'list':["Stop","Repeat","PingPong"]
                                }],
            ['destroy',
             'Destroy this object when animation completes. Stop mode only.'],
            ]
    _field_list += _animate_list
    #defaults
    _animation = ""
    fps = 15
    mode = "PingPong"
    destroy = False  
    
    frames = None  
    modes = {"Stop":Opioid2D.StopMode, "Repeat":Opioid2D.RepeatMode,
             "PingPong":Opioid2D.PingPongMode}
    set_action = None
    last_frame_info = None
                        
    @component_method
    def on_added_to_scene(self):
        """Animate when object is added to scene"""
        if self.frames:
            action = Opioid2D.Animate(self.frames, fps=self.fps, 
                                     mode=self.modes[self.mode])
            if self.destroy:
                action += Opioid2D.CallFunc(self.owner.destroy)
            self.owner.do(action)
        
    def get_frame_images(self):
        filename = os.path.split(self.folder)[1]
        path = os.path.join(self.folder,filename+"*.*")
        if self.last_frame_info == path:
            return self.frames
        frames = Opioid2D.ResourceManager.get_pattern(path)
        self.last_frame_info = path
        return frames
    
    def do_set_animation(self):
        frames = None
        self.set_action = None
        if self.folder:
            try:
                frames = self.get_frame_images()
            except:
                self._animation = None
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

    def set_anim_attr(self, attr, val):
        setattr(self, attr, val)
        if not getattr(Opioid2D.Director,"start_project",False):
            if self.set_action:
                return
            self.set_action = (Opioid2D.Delay(0)+ Opioid2D.CallFunc(
                                                self.do_set_animation)).do()
        else:
            self.do_set_animation()
    def get_anim_attr(self, attr):
        return getattr(self, attr)
                    
    folder = property(lambda s: s.get_anim_attr("_animation"),
                          lambda s, val: s.set_anim_attr("_animation", val) )
        
    @component_method            
    def on_delete(self):
        "Deconstruct component"
        if self.set_action:
            self.set_action.abort()
            
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
    
#    @component_method
#    def on_added_to_editor(self, scene):
#        """Show correct frame when object or component is added to editor"""
#        self.animation = self.folder    

    def on_removed_from_object(self):
        self.owner.set_image_file("art\\pug.png")

register_component( Animate_Folder)
