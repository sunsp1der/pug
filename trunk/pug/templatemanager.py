"""templatemanager.py

utility for storing customized pug templates for classes
"""

import copy

from pug.constants import *

class _TemplateManager(object):
    """_TemplateManager()
    
Singleton that stores template info for all objects.

stored in this form:
{<class>:
    {'templates': 
        {'template 1':templateobj1,
        'listo':templateobj2(named)},
    'default':'listo',
    'next_num' = 2} # unnamed template will be autonamed 'template 2'

note that the 'templates' dict will contain 'Raw', 'Raw Data', and 
'Raw Methods', which are all special auto-templates.
"""

    def __init__(self):
        self.templateDict = {
            'default_template_info':{
                'next_num':1, 
                'default':'Raw', 
                'templates':{'Raw':'Raw', 'Raw Data':'Raw Data', 
                                  'Raw Methods':'Raw Methods'}
             }
        }
    
_templateManager = _TemplateManager()

_aguiDefaultDict = {}

def get_template_manager():
    return _templateManager

def add_template( cls, template, setAsDefault=False):
    """add_template( cls, template, setAsDefault=False)
    
make template available to pug system for cls
"""
    if not isinstance(template,{}.__class__):
        raise TypeError("".join(["add_template() arg 2 must be a template:",
                                 str(template)]))
    templateDict = _templateManager.templateDict
    if not templateDict.has_key(cls):
        #defaults:
        templateDict[cls] = copy.deepcopy(templateDict['default_template_info'])
    entry = templateDict[cls]
    if not template.has_key('name'):
        template['name'] = ''.join(["Template ",str(entry['next_num'])])
        entry['next_num']+=1
    if not template.has_key('size'):
        template['size'] = PUGFRAME_DEFAULT_SIZE
    entry['templates'][template['name']] = template
    if setAsDefault:
        set_default_template(cls, template)
        
def set_default_template( cls, template):
    """make template the pug system default view for cls"""
    templateDict = _templateManager.templateDict
    templateDict[cls]['default'] = template['name']

def get_template_info( cls):
    templateDict = _templateManager.templateDict
    if templateDict.has_key(cls):
        return templateDict[cls]
    else:
        return {}
    
def get_agui_default_dict():
    return _aguiDefaultDict