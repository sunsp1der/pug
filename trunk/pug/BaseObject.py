"""A base pug object with all special features built in"""

import pug
from pug.util import get_code_file
from pug.code_storage import add_subclass_storageDict_key

class BaseObject(pug.GnamedObject, pug.ComponentObject):
    """BaseObject
    
Contains all special object features in pug:
GnamedObject: can have a global name (gname) so it can be located with
    pug.get_gnamed_object(gname)
ComponentObject: can use the pug component system
plus a few utility functions
"""
    def __init__(self, gname=''):
        pug.GnamedObject.__init__(self, gname=gname)
        pug.ComponentObject.__init__(self)
        
    def __del__(self):
        pug.GnamedObject.__del__(self)
        pug.ComponentObject.__del__(self)
        
    def _get_code_file(self):
        "_get_code_file(): try to return module filename for external editors"
        return get_code_file(self)
    
    _codeStorageDict = {}
    add_subclass_storageDict_key(_codeStorageDict, pug.GnamedObject)
    add_subclass_storageDict_key(_codeStorageDict, pug.ComponentObject)    