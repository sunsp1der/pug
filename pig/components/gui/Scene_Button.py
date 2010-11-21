import Opioid2D
from Opioid2D.utils.text import textbox
from Opioid2D.public.Node import Node

import pug
from pug.component import *

from pig.audio import get_sound
from pig.editor.agui import ScenesDropdown, SoundFile
from pig.PigDirector import PigDirector
from pig.components import SpriteComponent

class Scene_Button(SpriteComponent):
    """Turns object into a button that switches to a different scene when 
clicked."""
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [ 
            ['target',ScenesDropdown,{'doc':'Scene to switch to on click', 
                                     'component':True }],
            ['hover_look',pug.ColorPicker,{
        'doc':'Tint the button this color when mouse is over it'}],
            ['press_look',pug.ColorPicker,{
        'doc':'Tint the button this color when mouse is pressed on it'}],
            ['hover_sound',SoundFile,{
                            'doc':'Play this sound when mouse is hovering'}],
            ['click_sound',SoundFile,{
                            'doc':'Play this sound when mouse is clicked'}],
            ]
    #defaults
    target = None
    hover_look = (255, 255, 0)
    press_look = (255, 0, 0)
    hover_sound = None
    click_sound = None
    
    base_look = (255, 255, 255)
    hover_sound_object = None
    click_sound_object = None
    
    @component_method
    def on_first_display(self, register_type="single"):
        "Set up sounds and register for mouse events"
        self.hover_sound_object = get_sound(self.hover_sound)
        self.click_sound_object = get_sound(self.click_sound)
        self.base_look = self.owner.tint
        self.owner.mouse_register(register_type)
        
    @component_method
    def on_enter(self):
        "Show hover or press look"
        if self.owner in PigDirector.scene.mouse_manager._clicking:
            self.owner.tint = self.press_look
        else:
            self.owner.tint = self.hover_look
            self.hover_sound_object.play()
        
    @component_method
    def on_exit(self):
        "Show base look"
        self.owner.tint = self.base_look
        
    @component_method
    def on_click(self):
        "Switch scenes"
        PigDirector.switch_scene_to( self.target)
        self.click_sound_object.play()
        
    @component_method
    def on_press(self):
        "Show press look"
        self.owner.tint = self.press_look
               
register_component( Scene_Button)
