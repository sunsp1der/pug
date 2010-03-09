from pug.component import *
from pug import Filename
from pug.util import start_file

from pig import PigScene
from pig.audio import get_sound

class Open_File_On_Start( Component):
    """Open a file when the scene starts. Use default program to open it."""
    # component_info
    _set = 'pig'
    _type = 'utilities'
    _class_list = [PigScene]
    # attributes: ['name', 'doc', {extra info}]
    _field_list = [
        ["file", Filename, {'doc':"The file to open"}]
        ]
    #defaults
    file = None
    
    @component_method
    def on_start(self):
        "Open the file"
        start_file( self.file)        
        
register_component( Open_File_On_Start)