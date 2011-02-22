from Opioid2D import Mouse

from pug.component import *
from pug import Dropdown

from pig import Scene, get_gamedata
from pig.editor.agui import ScenesDropdown, SoundFile, PigImageBrowser
from pig import Director

class Set_Mouse_Cursor( Component):
    """Set the scene's mouse cursor."""
    # component_info
    _set = 'pig'
    _type = 'behavior'
    _class_list = [Scene]
    # attributes: ['name','desc'] or ['name', agui, {'doc':'desc', extra info}]
    _field_list = [
        ['image', PigImageBrowser,
            {'doc':'Image to use for mouse cursor. None = no mouse cursor.',
             'allow_delete':True}],
        ['hotspot',None,
            {'doc':'Hotspot location within image. (0 to 1,0 to 1)'}]
        ]
    #defaults
    image = None
    hotspot = (0,0)
    
    @component_method
    def on_start(self):
        "Get and play the sound object"
        self.original_cursor = Mouse.cursor
        Mouse.cursor = self.image 

    @component_method
    def on_exit(self):
        "Stop the sound"
        Mouse.cursor = self.original_cursor
        
register_component( Set_Mouse_Cursor)