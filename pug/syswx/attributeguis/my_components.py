"""MyComponents attribute gui"""

from pug.syswx.attributeguis.dropdown import Dropdown

class MyComponents (Dropdown):
    """Components on this object attribute GUI
    
This dropdown shows all the named components on the object and allows text 
entry as well.
    
MyComponents(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'component_types: only show named components of this type. This should be a
                        list of strings and/or component classes.
    '...': for more see Dropdown    
For kwargs optional arguments, see the Base attribute GUI
"""      
    return_strings = False
    def setup(self, attribute, window, aguidata): 
        aguidata.update({'list_generator': self.get_list,
                         'allow_typing':True,
                         })
        aguidata.setdefault('component_types',[])
        Dropdown.setup(self, attribute, window, aguidata)
        
    def get_list( self):
        component_list = []
        try:
            components = self.window.object.owner.components.get()
        except:
            return []
        component_types = self.aguidata['component_types']
        for component in components:
            if not component.gname or (component_types and \
                        component.__class__ not in component_types and \
                        component.__class__.__name__ not in component_types):
                continue
            component_list.append(component.gname)
        return component_list

                        