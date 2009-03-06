from weakref import proxy, ref as _ref
from new import instancemethod as _instancemethod
import inspect
import functools
import sys

from pug.component.component import *
all_components = None

_DEBUG = False

class ComponentObject(object):

    def __del__(self):
        if _DEBUG: print "ComponentObject.__del__"
        self.__components = None

    def __init__(self):
        self.__components = ComponentSet(self)

    def components(doc):
        """Returns the component set associated with this object."""
        def get_components(self):
            return self.__components
        return property(get_components, doc=doc)
    components = components(components.__doc__)
    _codeStorageDict = {
            'skip_attributes': ['__components']                        
                        }    
                
def component_method_wrapper(*args, **kwargs):
    retvalue = None
    obj = kwargs.pop('___obj_ref')()
    if not obj:
        return
    ___original_method = kwargs.pop('___original_method')
    method_list = kwargs.pop('___component_methods')
    for method in method_list:
        if method:
            if _DEBUG: print method, args, kwargs
            if not method.im_self.enabled:
                continue
            if method._ComponentMethod__has_kwargs:
                if method._ComponentMethod__has_args:
                    retvalue = method(*args, **kwargs)
                else:
                    retvalue = method(
                        *(args[:method._ComponentMethod__maxargs]), **kwargs)
            else:
                fixed_args = args[:]
                methodargs = method._ComponentMethod__args
                methoddefaults = method._ComponentMethod__defaults
                n = len(fixed_args) + 1
                while n < method._ComponentMethod__minargs:
                    if kwargs.has_key(methodargs[n]):
                        arg = kwargs[methodargs[n]]
                    else:
                        continue
#                    elif n + 1 > len(methodargs) - len(methoddefaults):
#                        arg = methoddefaults[n - len(methodargs) + \
#                                                   len(methoddefaults) + 1]
#                    else:
#                        arg= None
                    fixed_args += (arg,)
                    n=n+1
                while n < len(methodargs):
                    if kwargs.has_key(methodargs[n]):
                        arg = kwargs[methodargs[n]]
                    else:
                        break
#                        arg = None
                    fixed_args += (arg,)
                    n = n+1                    
                if method._ComponentMethod__has_args:
                    retvalue = method(*fixed_args)
                else:
                    retvalue = method(
                                *fixed_args[:method._ComponentMethod__maxargs])
    if ___original_method:
        retvalue = ___original_method( obj, *args, **kwargs)
    return retvalue

#TODO: run_component_method
#def run_component_method( method, args, kwargs):
#    try:
#        retvalue = method(*args, **kwargs)
#    except:
#        print \
#"""I'd like to take the component processor part off the stack here, so that 
#an exception would not show run_component_method or component_method_wrapper in
#the traceback. But I can't figure out how... 
#"""
#    else:
#        return retvalue

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
        global all_components
        if not all_components:
            all_components = __import__("all_components")

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
        return component
    
    def get(self, comp=None):
        """get(comp=None)->list of components of class comp or with name comp
        
If comp is None, return all components. If comp is a string, search by class 
name. Otherwise search by class."""
        compname = compclass = None
        if type(comp) == str:
            compname = comp
        else:
            compclass = comp
        if compclass:
            if not issubclass(compclass, Component):
                raise TypeError(''.join([compclass," is not a component"]))
        components = self.__component_list.get_components()
        if comp is None:
            return components[:]
        else:
            complist = []
            if compclass:
                for c in components:
                    if isinstance(c, compclass):
                        complist.append(c)
            else:
                for c in components:
                    if c.__class__.__name__ == compname:
                        complist.append(c)
            return complist

    def get_one(self, comp):
        "get_one(comp)->First element in list returned by get(comp)"
        for b in self.get(comp):
            return b

    def remove(self, component):
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
                    setattr(obj, name, original_method)
                else:
                    delattr(obj, name)
                del original_methods[name]
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
        
