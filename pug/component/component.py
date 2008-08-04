from inspect import CO_VARARGS as _CO_VARARGS, \
    CO_VARKEYWORDS as _CO_VARKEYWORDS, getargspec as _getargspec
from new import code as _code, function as _function, \
    instancemethod as _instancemethod
from types import MethodType as _MethodType

# TODO: make classlist work
# TODO: make attributeList work

class Component(object):
    """Component - pug uses components to add python code to objects at runtime
    
Class attributes:        
_Type: a string denoting the general type of component (i.e. 'Mouse' for 
        components having to do with mouse controls).  Use a '/' to denote a 
        sub-type if you want. Standard is first letter capital, as short a
        string as possible.
_Set: a string with the name of the set that this component comes from 
        (i.e if it were a bunch of shoot-em-up behaviors, you might call the set
        'shooter' or 'shoot_em_up' or even "Bart's shooter pack")
_ClassList: a list of classes that this component is meant to work with.
        This is only checked by the pug system, using isinstance. Pug will also
        check to see if an object has a 'componentClassList' attribute, which
        can contain a list of classes that the object is compatible with for
        component usage.
_attributeList: attributes (can include methods) that will be shown in the 
        default component view in the pug system. Default is to show all non-
        private attributes, but no methods.  Methods can be viewed in the 
        Component Methods view.
component_method: methods in a component with this decorator are made available
        to the object with this component
"""    
    _Type = None
    _Set = None
    _ClassList = []

    def _component_method_names(doc):

        """Returns a generator of component method names."""

        def get_component_method_names(self):
            cls = self.__class__
            return (k for k in dir(cls) \
                    if isinstance(getattr(cls, k), ComponentMethod))
        return property(get_component_method_names, doc=doc)
    _component_method_names = \
        _component_method_names(_component_method_names.__doc__)
		
class ComponentList(object):

    def __del__(self):
        self.__components = None
        self.__methods = None

    def __init__(self):
        self.__components = []
        self.__methods = {}

    def add(self, component):
        assert isinstance(component, Component)
        methods = self.__methods
        for key in component._component_method_names:
            value = getattr(component, key)
            component_methods = methods.get(key)
            if component_methods is None:
                component_methods = []
                methods[key] = component_methods
            component_methods.append(value)
        self.__components.append(component)

    def get_components(self):
        return self.__components

    def get_methods(self, key):
        return self.__methods.get(key)

    def get_method_names(self):
        return self.__methods.keys()

    def remove(self, component):
        self.__components.remove(component)
        methods = self.__methods
        for key in component._component_method_names:
            value = getattr(component, key)
            methods_list = methods[key]
            methods_list.remove(value)
            if not len(methods_list):
                del methods[key]

class ComponentMethod(object):

    def __del__(self):
        self.__cache = None
        self.__func = None

    def __get__(self, instance, cls):
        if instance is None:
            return self
        cache = self.__cache
        instance_id = id(instance)
        bound_method = cache.get(instance_id)
        if bound_method is None:
            bound_method = _instancemethod(self.__func, instance, cls)

            #def bound_method(*args, **kw_args):
            #    return self.__func(instance, *args, **kw_args)

            cache[instance_id] = bound_method
        return bound_method

    def __init__(self, func):
        code = func.func_code
        flags = code.co_flags
        locals = code.co_nlocals
        n = code.co_argcount
        names = list(code.co_varnames)
        if not (flags & _CO_VARKEYWORDS):
            flags |= _CO_VARKEYWORDS
            locals += 1
            names.append('')
        if not (flags & _CO_VARARGS):
            flags |= _CO_VARARGS
            locals += 1
            names.insert(-1, '')
        new_code = _code(n, locals, code.co_stacksize, flags, code.co_code,
                         code.co_consts, code.co_names, tuple(names),
                         code.co_filename, code.co_name, code.co_firstlineno,
                         code.co_lnotab)
        self.__cache = {}
        self.__func = _function(new_code, func.func_globals, func.func_name,
                                func.func_defaults, func.func_closure)

component_method = ComponentMethod
