import os

import Opioid2D
from Opioid2D.public.Node import Node

from pug import Filename, Dropdown
from pug.component import *
from pug.util import standardize_path, destandardize_path

from pig.components import SpriteComponent
from pig.editor.agui import PigImageBrowser

class Animate_Folder(SpriteComponent):
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
            ['old_image', PigImageBrowser, 
                    {'doc': 'Image to return to if this component is removed'}]
            ]
    _field_list += _animate_list
    #defaults
    _animation = ""
    fps = 15
    mode = "PingPong"
    destroy = False  
    old_image = None
    
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
        filename = destandardize_path(os.path.split(self.folder)[1])
        path = os.path.join(destandardize_path(self.folder),filename+"*.*")
        if self.last_frame_info == path:
            return self.frames
        frames = Opioid2D.ResourceManager.get_pattern(path)
        self.last_frame_info = path
        return frames
    
    def do_set_animation(self):
        self.set_action = None
        frames = None 
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
                    pass
            else:
                self.frames = frames
        else:
            self.restore_old_image()
        if not self.frames:
            self.frames = None
            self.last_frame_info = None
        if not getattr(Opioid2D.Director,"start_project", False):
            self.show_editor_frame()

    def set_anim_attr(self, attr, val):
        setattr(self, attr, val)
        if not getattr(Opioid2D.Director,"start_project", False):
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
        try:
            self.restore_old_image()
        except:
            pass
        if self.set_action:
            self.set_action.abort()
            
    def show_editor_frame(self, imagenum=None):
        if self.owner:
            if self.folder and self.frames: 
                if imagenum is None:
                    imagenum = len(self.frames)/2
                old_image = self.owner.image_file
                try:
                    self.owner.image_file = self.frames[imagenum]  
                except:
                    if self.owner.image_file:
                        self.old_image = self.owner.image_file
                    self.restore_old_image()
                else:
                    import wx
                    wx.CallAfter(wx.GetApp().refresh)
                    if self.old_image is None:
                        try:    
                            self.old_image = standardize_path( old_image)
                        except:
                            pass
            else:
                self.restore_old_image()
    
    def on_removed_from_object(self):
        self.restore_old_image()
        
    def on_added_to_object(self):
        try:
            self.old_image = standardize_path(self.owner.image_file)
        except:
            pass
        try:
            (Opioid2D.Delay(0)+ Opioid2D.CallFunc( self.do_set_animation)).do()
        except:
            pass
        
    def restore_old_image(self):
        if not self.owner:
            return
        if self.old_image:
            try:
                self.owner.set_image_file( self.old_image)
            except:
                self.owner.set_image_file("art/pug.png")
        else:
            self.owner.set_image_file("art/pug.png")
        if getattr(Opioid2D.Director, "viewing_in_editor", False):
            import wx
            wx.CallAfter(wx.GetApp().refresh)                        

register_component( Animate_Folder)
