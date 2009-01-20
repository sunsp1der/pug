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
    def setup(self, attribute, window, aguidata):    
        specialaguidata = {'allow_typing': True, 
                            'list_generator': self.list_generator_func}
        specialaguidata.update(aguidata)
        self.class_list = aguidata.get('class_list',[])
        Dropdown.setup(self, attribute, window, specialaguidata)
        
    def list_generator_func(self):
        return get_gnames(tuple(self.class_list))