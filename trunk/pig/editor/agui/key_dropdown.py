"""ObjectsDropdown attribute gui"""

from pug.syswx.attributeguis.dropdown import Dropdown

import pig.keyboard

class KeyDropdown (Dropdown):
    """PIG object selection attribute GUI
    
KeypressDropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'as_character': Store info as a character, not a number. Default is True
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""      
    return_strings = False
    def setup(self, attribute, window, aguidata): 
        aguidata.setdefault('as_character', True)
        aguidata.setdefault('sort', False)
        if aguidata['as_character']:
            keylist = []
            for pair in pig.keyboard.key_list:
                keylist.append(pair[0])
            aguidata['list'] = keylist
        else:
            aguidata['list'] = pig.keyboard.key_list
        Dropdown.setup(self, attribute, window, aguidata)
        
                        