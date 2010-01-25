"""ObjectsDropdown attribute gui"""

from pug.syswx.attributeguis.dropdown import Dropdown

from pig.keyboard import *

class KeyDropdown (Dropdown):
    """PIG object selection attribute GUI
    
KeypressDropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'class_list': a list of acceptable object classes. If this is empty or 
        non-existent, all Opioid2D.Node objects will be listed as options.
    'append_list': a list of ("name",obj) options to add to end of list.
    'prepend_list': a list of ("name",obj) options to add to start of list.
    'none_choice': if value is -1, adds 'append_list':[('#None#',None)],
        otherwise if value evaluates to True, 'prepend_list':[('#None#',None)]
    'component': if True, sets 'none_choice':True and returns strings rather
        or None than actual classes. Used for component fields
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""      
    return_strings = False
    def setup(self, attribute, window, aguidata): 
        aguidata['list'] = [("None", None)] + key_list
        Dropdown.setup(self, attribute, window, aguidata)
        
                        