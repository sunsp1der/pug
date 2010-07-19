import os.path

from pygame import font

import Opioid2D
from Opioid2D.utils.text import textbox
from Opioid2D.public.Node import Node

from pug import Filename
from pug.component import *
from pug.syswx.util import show_exception_dialog

class Textbox(Component):
    "Create text for this object's image"
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['text','Text to display'],
            ['font_file',Filename,{'doc':'Font to use', 'subfolder':'art',
                              'wildcards':"truetype font (*.ttf)|*.ttf"}],
            ['font_size','The point size of the font'],
            ['max_width','The maximum text width in pixels'],
            ]
    #defaults
    __text = 'text'
    __font_file = None
    font = None
    __max_width = None
    __font_size = 32
    
    def set_font_size(self, font_size):
        self.__font_size = font_size
        self.set_font_file()
        self.set_text()
    def get_font_size(self):
        return self.__font_size
    font_size = property(get_font_size, set_font_size)
    
    def set_max_width(self, max_width):
        self.__max_width = max_width
        self.set_text()
    def get_max_width(self):
        return self.__max_width
    max_width = property(get_max_width, set_max_width)
    
    @component_method
    def set_text(self, text=None):
        "Set the text to display"
        if text is None:
            text=self.text
        self.__text = text
        image = textbox( self.font, text, self.max_width) 
        if self.owner:
            (Opioid2D.Delay(0) + \
             Opioid2D.CallFunc(Opioid2D.Sprite.set_image, 
                               self.owner, image)).do() 
            self.owner.image_file = None
               
    @component_method
    def get_text(self):
        "Get the displayed text"
        return self.__text
    text = property(get_text, set_text)
    
    def set_font_file(self, font_file=None, font_size=None):
        if font_file is None:
            font_file = self.__font_file
        else:
            self.__font_file = font_file
        if font_size is None:
            font_size = self.__font_size
        else:
            self.__font_size = font_size
        try:
            self.font = font.Font(font_file, self.__font_size)
        except:
            self.font = self.__class__.font
            self.__font_file = self.__class__.__font_file
        self.set_text()
    def get_font_file(self):
        return self.__font_file
    font_file = property(get_font_file, set_font_file)
    
    @component_method
    def on_added_to_scene(self, scene):
        """Show text when object is added to scene"""
        self.set_text()
        
    @component_method
    def on_added_to_editor(self, scene):
        """Show text when object or component is added to editor"""
        self.set_text()    

    def on_added_to_object(self):
        self.on_added_to_editor( Opioid2D.Director.scene)

    def __init__(self, *a, **kw):
        if self.__class__.font is None:
            try:
                defaultfont = os.path.join("art","accid___.ttf")
                self.__class__.font = font.Font(defaultfont,
                                                self.__class__.__font_size)
                self.__class__.__font_file = defaultfont
            except:
                self.__class__.font = font.Font(None, 
                                                self.__class__.__font_size)
                self.__class__.__font_file = None
        if self.__max_width is None:
            self.__class__.__max_width = Opioid2D.Display.get_resolution()[0]
        Component.__init__(self, *a, **kw)

register_component( Textbox)
