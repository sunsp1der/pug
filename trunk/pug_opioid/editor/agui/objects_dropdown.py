"""ObjectsDropdown attribute gui"""

from Opioid2D.public.Node import Node

from pug.gname import get_gnames
from pug.syswx.attributeguis.dropdown import Dropdown

from pug_opioid.util import get_available_objects

class ObjectsDropdown (Dropdown):
    """Pug_Opioid object selection attribute GUI
    
ObjectsDropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'class_list': a list of acceptable object classes. If this is empty or 
        non-existent, all Opioid2D.Node objects will be listed as options.
    'append_list': a list of ("name",obj) options to add to end of list.
    'prepend_list': a list of ("name",obj) options to add to start of list.
    'none_choice': if value is -1, shortcut for 'prepend_list':[('#None#',None)],
        otherwise if value evaluates to True, 'append_list':[('#None#',None)]
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""      
    def setup(self, attribute, window, aguidata):    
        specialaguidata = {'class_list': [Node],
                           'append_list':[],
                           'prepend_list':[],
                           'doc': 'Saved object class', 
                            'list_generator': self.object_list_generator}
        specialaguidata.update(aguidata)
        none_choice = specialaguidata.get('none_choice')
        if none_choice == -1:
            specialaguidata['append_list'].append(('#None#',None))
        else:
            specialaguidata['prepend_list'].insert(0,('#None#',None))
        specialaguidata['prepend_list'].reverse()
        self.class_list = aguidata.get('class_list',[])
        Dropdown.setup(self, attribute, window, specialaguidata)
        
    def object_list_generator(self):
        objdict = get_available_objects()
        objlist = objdict.values()
        objlist.sort()
        for item in self.aguidata['prepend_list']:
            objlist.insert(0, item)
        for item in self.aguidata['append_list']:
            objlist.append(item)
        return objlist    
                        