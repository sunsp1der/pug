"ScoreText.py"
from Opioid2D.public.Node import Node

from pug import Filename, Text
from pug.component import *

from pig.components import Textbox
from pig.util import GameData

class ScoreText(Textbox):
    "Show score from GameData"
    #component_info
    _set = 'pig'
    _type = 'gui'
    _class_list = [Node]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
            ['prefix',Text,{
                'doc':'Score value will have this written before the number'}],
            ['default',Text,{'doc:':'Text to display in editor\n'+\
                             '(prefix added automatically)'}],
            ['font_file',Filename,{'doc':'Font to use', 'subfolder':'art',
                              'wildcards':"truetype font (*.ttf)|*.ttf"}],
            ['font_size','The point size of the font'],
            ['max_width','The maximum text width in pixels'],
            ]
    #defaults
    __default = '000'
    __prefix = 'Score: '
        
    @component_method
    def on_added_to_scene(self, scene):
        """Set score to zero unless otherwise set"""
        GameData.register_callback( "score", self.on_score_change)
        if getattr(GameData, "score", None) is None:
            GameData.score = 0
            
    def on_score_change(self, *a, **kw):
        self.set_text()            
            
    @component_method
    def set_text(self, text=None):
        "Show current score"
        if text is None:
            if getattr(GameData, "score", None) is None:
                text = self.prefix + self.default
            else:
                text = self.prefix + str(getattr(GameData,"score",self.default))
        Textbox.set_text( self, text)
        
    def set_default(self, default):
        self.__default = default
        self.set_text()
    def get_default(self):
        return self.__default
    default = property(get_default, set_default)
    
    def set_prefix(self, prefix):
        self.__prefix = prefix
        self.set_text()
    def get_prefix(self):
        return self.__prefix
    prefix = property(get_prefix, set_prefix)            
                
        
register_component( ScoreText)
