"""manager.py

contains the pug system's component manager
"""
import imp, sys
from time import time

import pug
from pug.component.component import Component

all_components = imp.new_module('all_components')
sys.modules['all_components'] = all_components

class _GlobalComponentManager():
    """The component manager is used to register all components available for
adding through the pug system"""
    def __init__(self):
        # componentName:componentObject
        self.componentList = []
        self.lastUpdate = 0
       
global _globalComponentManager
_globalComponentManager = _GlobalComponentManager() 
del _GlobalComponentManager
 
def register_component( component):
    """register_component( component)
    
component: the component, defined as a class derived from Component
    
Register a component class with the component manager. This makes the component
available through the pug system.
"""
    if not issubclass(component,Component):
        raise TypeError("".join(["Not a Component:",str(component)]))
    if component in _globalComponentManager.componentList:
        return
    component._setup_method_names()
    _globalComponentManager.componentList.append(component)
    _globalComponentManager.lastUpdate = time()
    setattr(all_components, component.__name__, component)
        
def get_component_manager():
    return _GlobalComponentManager

def get_component_list():
    x = _globalComponentManager.componentList[:]
    return x

def get_last_component_update():
    return _globalComponentManager.lastUpdate    