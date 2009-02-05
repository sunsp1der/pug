from weakref import ref as _ref
import inspect
import functools

from pug.component.component import *
all_components = None

_DEBUG = False

class ComponentObject(object):

    def __del__(self):
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
    if not kwargs.pop('___obj_ref')():
        return
    ___original_method = kwargs.pop('___original_method')
    for method in kwargs.pop('___component_methods'):
        if method:
            if _DEBUG: print method, args, kwargs
            if not method.im_self.enabled:
                continue
            if method._ComponentMethod__has_kwargs:
                if method._ComponentMethod__has_args:
                    method(*args, **kwargs)
                else:
                    method(*(args[:method._ComponentMethod__maxargs]), **kwargs)
            else:
                fixed_args = args[:]
                methodargs = method._ComponentMethod__args
                methoddefaults = method._ComponentMethod__defaults
                n = len(fixed_args) + 1
                while n < method._ComponentMethod__minargs:
                    if kwargs.has_key(methodargs[n]):
                        arg = kwargs[methodargs[n]]
                    elif n + 1 > len(methodargs) - len(methoddefaults):
                        arg = methoddefaults[n - len(methodargs) + \
                                                   len(methoddefaults) + 1]
                    else:
                        arg= None
                    fixed_args += (arg,)
                    n=n+1
                while n < len(methodargs):
                    if kwargs.has_key(methodargs[n]):
                        arg = kwargs[methodargs[n]]
                    else:
                        arg = None
                    fixed_args += (arg,)
                    n = n+1                    
                if method._ComponentMethod__has_args:
                    method(*fixed_args)
                else:
                    method(*fixed_args[:method._ComponentMethod__maxargs])
    if ___original_method:
        return ___original_method(*args, **kwargs)                

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
            component_methods = list(component_list.get_methods(name))
            original_method = original_methods.get(name, sentinel)
            if original_method is sentinel:
                original_method = getattr(obj, name, None)
                original_methods[name] = original_method
            wrapper = functools.partial(component_method_wrapper,                             
                            ___obj_ref=self.__obj, 
                            ___component_methods=component_methods,
                            ___original_method=original_method)
            if original_method:
                functools.update_wrapper(wrapper, original_method)
            setattr(obj, name, wrapper)
        return component
    
    def get(self, cls=None):
        if type(cls) == str:
            if all_components:
                cls = getattr(all_components, cls, cls)
        if cls is not None and not issubclass(cls, Component):
            raise TypeError(''.join([cls," is not a component"]))
        components = self.__component_list.get_components()
        if cls is None:
            return components[:]
        else:
            complist = []
            for b in components:
                if isinstance(b, cls):
                    complist.append(b)
            return complist

    def get_one(self, cls):
        for b in self.get(cls):
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
        
