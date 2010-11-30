from weakref import proxy, ref as _ref
from new import instancemethod as _instancemethod
import inspect
import functools
import sys

from pug.component.component import *

_DEBUG = False

class ComponentObject(object):
    __components = None
    def __del__(self):
        if _DEBUG: print "ComponentObject.__del__"
        self.__components = None

    def __init__(self):
        self.__components = ComponentSet(self)

    def get_components(self):
        return self.__components
    components = property(get_components,
                doc="Components attached to this object.")

    _codeStorageDict = {
            'skip_attributes': ['__components']                        
                        }    
                
def component_method_wrapper(*args, **kwargs):
    retvalue = None
    obj = kwargs.pop('___obj_ref')()
#    if not obj:
#        return
    original_method = kwargs.pop('___original_method')
    method_list = kwargs.pop('___component_methods')
    for method in method_list:
        if method:
#            if _DEBUG: print method, args, kwargs
            if not method.im_self.enabled:
                continue
            retvalue =  method(*args,**kwargs)
    if original_method:
        try:
            retvalue = original_method( obj, *args, **kwargs)
        except:
            # hack
            # we hit this sometimes if an object's class has been changed
            original_method = getattr(obj.__class__, original_method.__name__)
            retvalue = original_method( obj, *args, **kwargs)
    return retvalue

class ComponentSet(object):

    __sentinel = object()

    def __del__(self):
        self.__component_list = None
        self.__obj = None
        self.__original_methods = None

    def __init__(self, obj):
        self.__component_list = ComponentList()
        self.__obj = _ref(obj)
        self.__original_methods = {}

    def add(self, component):
        """add(component)->component instance

Adds component to the object.  

component: component instance or component class. If it's an instance it will 
simply be added. If it's a class, an instance will be created and added.
"""

        if not isinstance(component, Component):
            try:
                is_component_class = issubclass(component, Component)
            except TypeError:
                is_component_class = False
            if not is_component_class:
                raise TypeError(message=''.join(['ComponentList.add: ',
                                             str(component), 
                                             "is not a component"]))
            component = component()
        component_list = self.__component_list
        component_list.add(component)
        obj = self.__obj()
        component.owner = obj
        original_methods = self.__original_methods
        sentinel = self.__sentinel
        for name in component._component_method_names:
            component_methods = component_list.get_methods(name)
            original_method = original_methods.get(name, sentinel)
            if original_method is sentinel:
                original_method = getattr(obj, name, None)
                if type(original_method) is _instancemethod:
                    # if we store an instancemethod, owner won't delete properly
                    original_method = getattr(original_method.im_class, name)
                original_methods[name] = original_method
            if original_method:
                method_proxy = weakref.proxy(original_method) 
            else:
                method_proxy = None
            wrapper = functools.partial(component_method_wrapper,                             
                            ___obj_ref=self.__obj, 
                            ___component_methods=component_methods,
                            ___original_method=method_proxy)
            if original_method:
                functools.update_wrapper(wrapper, original_method)
            setattr(obj, name, wrapper)
        try:
            component.on_added_to_object()
        except:
            pass
        return component
    
    def get(self, comp=None, gname=None):
        """get(comp=None, gname=None)->list of specified components 
        
Return a list of components with class==comp (a string of the component name 
will work also) and gname==gname.
If comp and gname are both None, return all components on the object.
"""
        compname = compclass = None
        if type(comp) == str:
            compname = comp
        else:
            compclass = comp
        if compclass:
            if not issubclass(compclass, Component):
                raise TypeError(''.join([compclass," is not a component"]))
        components = self.__component_list.get_components()
        complist = []
        if comp is None and gname is None:
            # no component or gname specified. Return all.
            return components[:]
        elif comp is None:
            # just check gname
            for c in components:
                if gname == c.gname:
                    complist.append(c)
        else:
            # check component class and gname, if provided
            if compclass:
                for c in components:
                    if isinstance(c, compclass) and gname and gname==c.gname:
                        complist.append(c)
            elif compname:
                for c in components:
                    if c.__class__.__name__ == compname and gname \
                                                        and gname==c.gname:
                        complist.append(c)
        return complist

    def get_one(self, comp=None, gname=None):
        "get_one(comp)->First element in list returned by get(comp)"
        for b in self.get(comp, gname):
            return b

    def remove(self, component):
        try:
            component.on_removed_from_object()
        except:
            pass
        component_list = self.__component_list
        if component not in component_list.get_components():
            return False
        component_list.remove(component)
        obj = self.__obj()
        original_methods = self.__original_methods
        for name in component._component_method_names:
            component_methods = component_list.get_methods(name)
            if component_methods is None:
                original_method = original_methods[name]
                if original_method is not None:
                    # fancy rebind to original method... I don't totally get it
                    setattr(obj, name, original_method.__get__(obj, 
                                                               obj.__class__))
                else:
                    delattr(obj, name)
                original_methods.pop(name)
        return True
                
    def remove_duplicate_of(self, component):
        comp = self.get_duplicate_of(component)
        if comp:
            self.remove(comp)
        return comp
    
    def get_duplicate_of(self, component):
        for mycomponent in self.__component_list.get_components():
            if mycomponent.is_duplicate_of( component):
                return mycomponent
        return None
        
