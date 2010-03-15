"""ObjectsDropdown attribute gui"""

from pug.syswx.attributeguis.dropdown import Dropdown

class GroupDropdown (Dropdown):
    """PIG group selection attribute GUI
    
This dropdown can be used to track the groups used by objects in a scene.
It is intended to be used with with components that have a group attribute.
See pig.components.collision.Join_Group for example usage.
    
GroupDropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    '...': for more see Dropdown    

For kwargs optional arguments, see the Base attribute GUI
"""      
    return_strings = False
    def setup(self, attribute, window, aguidata): 
        aguidata.update({'list_generator': get_group_list,
                         'allow_typing':True})
        Dropdown.setup(self, attribute, window, aguidata)

group_dict = {}
DEFAULT_GROUP = "colliders"

def register_group( tag, group):
    """register_group( tag, group)
    
tag: a unique tag. Usually a tuple: (ref to component object, attribute)
group: the group name. If group == None, tag will be deleted from dict
"""
    if group == DEFAULT_GROUP:
        pass
    elif group is None:
        group_dict.pop(tag, None)
    else:
        group_dict[tag] = group
        
def get_group_list():
    group_list = [DEFAULT_GROUP]
    last_group = ""
    groups = group_dict.values()
    groups.sort()
    for group in groups:
        if last_group != group:
            group_list.append(group)
            last_group = group
    return group_list

                        