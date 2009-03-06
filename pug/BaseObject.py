"""A base pug object with all special features built in"""

import pug
from pug.code_storage import add_subclass_skip_attributes

class BaseObject(pug.GnamedObject, pug.ComponentObject):
    """BaseObject
    
Contains all special object features in pug:
GnamedObject: can have a global name (gname) so it can be located with
    pug.get_gnamed_object(gname)
ComponentObject: can use the pug component system
"""
    def __init__(self, gname=''):
        pug.GnamedObject.__init__(self, gname=gname)
        pug.ComponentObject.__init__(self)
        
    def __del__(self):
        pug.GnamedObject.__del__(self)
        pug.ComponentObject.__del__(self)

    _codeStorageDict = {}
    add_subclass_skip_attributes(_codeStorageDict, pug.GnamedObject)
    add_subclass_skip_attributes(_codeStorageDict, pug.ComponentObject)    