"""GnamedObject attribute gui"""

import wx
import wx.combo

from pug.gname import get_gnames
from pug.syswx.attributeguis.dropdown import Dropdown

class GnameDropdown (Dropdown):
    """Gnamed object selection attribute GUI
    
GnamedObject(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'class_list': a list of acceptable gnamed object classes. If this is empty 
    or non-existent, all gnamed objects will be listed as options.
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        special_aguidata = {'allow_typing': True, 
                            'list_generator': self.list_generator_func}
        special_aguidata.update(aguidata)
        self.class_list = aguidata.get('class_list',[])
        Dropdown.__init__(self, attribute, window, special_aguidata, **kwargs)
        
    def list_generator_func(self):
        return get_gnames(tuple(self.class_list))