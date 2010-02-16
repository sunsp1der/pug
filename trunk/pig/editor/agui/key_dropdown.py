"""ObjectsDropdown attribute gui"""

from pug.syswx.attributeguis.dropdown import Dropdown

from pig.keyboard import *

class KeyDropdown (Dropdown):
    """PIG object selection attribute GUI
    
KeypressDropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""      
    return_strings = False
    def __init__(self, attribute, window, aguidata): 
        aguidata['list'] = [("None", None)] + key_list
        Dropdown.__init__(self, attribute, window, aguidata)
        
                        