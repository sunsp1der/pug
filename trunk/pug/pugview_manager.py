"""pugview_manager.py

utility for storing customized pug pugviews for classes
"""

import copy
import inspect

from pug.constants import *

class _PugviewManager(object):
    """_PugviewManager()
    
Singleton that stores pugview info for all objects.

stored in this form:
{<class>:
    {'pugviews': 
        {'pugview 1':pugviewobj1,
        'listo':pugviewobj2(named)},
    'default':'listo',
    'next_num' = 2} # unnamed pugview will be autonamed 'pugview 2'

note that the 'pugviews' dict will contain 'Raw', 'Raw Data', and 
'Raw Methods', which are all special auto-pugviews.
"""

    def __init__(self):
        self.pugviewDict = {
            'default_pugview_info':{
                'next_num':1, 
                'default':'Raw', 
                'pugviews':{'Raw':'Raw', 'Raw Data':'Raw Data', 
                                  'Raw Methods':'Raw Methods'}
             }
        }
    
_pugviewManager = _PugviewManager()

_aguiDefaultDict = {}

def get_pugview_manager():
    return _pugviewManager

def get_obj_pugview_info( obj):
    """get_pugview_info( obj)->pugviewInfo dict for obj"""
    pugviewInfo = None
    # look for pugviews specific to object's class
    if hasattr(obj,'__class__'):
        pugviewInfo = get_pugview_info( obj.__class__)
    # if necessary, look for pugviews assigned to object
    if not pugviewInfo and not inspect.isclass(obj) and \
                hasattr(obj, '_pug_pugview_class'):
        pugviewInfo = get_pugview_info(obj._pug_pugview_class)
    # as a last resort, use the default pugview
    if not pugviewInfo:
        pugviewInfo = get_pugview_info('default_pugview_info')
    return pugviewInfo    

def get_default_pugview( obj):
    """get_default_pugview( obj)->default pug pugview for obj"""
    info = get_obj_pugview_info(obj)
    if info.has_key('default'):
        return info['pugviews'][info['default']]
    return None

def add_pugview( cls, pugview, setAsDefault=False):
    """add_pugview( cls, pugview, setAsDefault=False)
    
make pugview available to pug system for cls
"""
    if not isinstance(pugview,{}.__class__):
        raise TypeError("".join(["add_pugview() arg 2 must be a pugview:",
                                 str(pugview)]))
    pugviewDict = _pugviewManager.pugviewDict
    if not pugviewDict.has_key(cls):
        #defaults:
        pugviewDict[cls] = copy.deepcopy(pugviewDict['default_pugview_info'])
    entry = pugviewDict[cls]
    if not pugview.has_key('name'):
        pugview['name'] = ''.join(["Pugview ",str(entry['next_num'])])
        entry['next_num']+=1
    if not pugview.has_key('size'):
        pugview['size'] = PUGFRAME_DEFAULT_SIZE
    entry['pugviews'][pugview['name']] = pugview
    if setAsDefault:
        set_default_pugview(cls, pugview)
        
def set_default_pugview( cls, pugview):
    """make pugview the pug system default view for cls"""
    pugviewDict = _pugviewManager.pugviewDict
    pugviewDict[cls]['default'] = pugview['name']

def get_pugview_info( cls):
    pugviewDict = _pugviewManager.pugviewDict
    if pugviewDict.has_key(cls):
        return pugviewDict[cls]
    else:
        return {}
    
def get_agui_default_dict():
    return _aguiDefaultDict