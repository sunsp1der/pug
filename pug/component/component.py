from inspect import CO_VARARGS as _CO_VARARGS, \
    CO_VARKEYWORDS as _CO_VARKEYWORDS, getargspec as _getargspec
from new import code as _code, function as _function, \
    instancemethod as _instancemethod
from types import MethodType as _MethodType

from pug.code_storage.constants import _INDENT

# TODO: make classlist work
# TODO: make attributeList work

class Component(object):
    """Component( **kwargs)
    
Pug uses components to add python code to objects at runtime

kwargs: Component.__init__ will assign kwargs as attributes. For example...
MyComponent( size=10, name='biggy') 
When MyComponent is created, an attribute 'size' will be created with value 10
and an attribute 'name' will be created with value 'biggy'
    
    
Class attributes:        
_set: a string with the name of the set that this component comes from 
        (i.e if it were a bunch of shoot-em-up behaviors, you might call the set
        'shooter' or 'shoot_em_up' or even "Bart's shooter pack")
_type: a string denoting the general type of component (i.e. 'Mouse' for 
        components having to do with mouse controls).  Use a '/' to denote a 
        sub-type if you want. Standard is first letter capital, as short a
        string as possible.
_class_list: a list of classes that this component is meant to work with.
        This is only checked by the pug system, using isinstance. Pug will also
        check to see if an object has a 'componentClassList' attribute, which
        can contain a list of classes that the object is compatible with for
        component usage.
_attribute_dict: Dictionary of attribute:docstring. This is a dictionary of the
        official attributes of the Component. These are the attributes that will
        be serialized when the component is saved, and are the attributes that 
        will be shown in pug's default component view. docstring can be left
        blank, but it's nice to provide info about attributes.
*Other: component attribute defaults should be set at the class level.
@component_method: methods in a component with this decorator are made available
        to the object with this component
"""    
    _set = None
    _type = None
    _class_list = []
    _attribute_dict = {}
    
    def __init__(self, **kwargs):
        for attr, val in kwargs.iteritems():
            setattr(self, attr, val)
                            
    def _component_method_names(doc):

        """Returns a generator of component method names."""

        def get_component_method_names(self):
            cls = self.__class__
            return (k for k in dir(cls) \
                    if isinstance(getattr(cls, k), ComponentMethod))
        return property(get_component_method_names, doc=doc)
    _component_method_names = \
        _component_method_names(_component_method_names.__doc__)
		
    def _create_object_code(self, storageDict, indentLevel, exporter):
        if storageDict['as_class']:
            return exporter.create_object_code(self, storageDict, indentLevel, 
                                               exporter)
        else:
            storage_name = storageDict['storage_name']
            baseIndent = _INDENT * indentLevel
            code = []
            code += [baseIndent,storage_name," = ",self.__class__.__name__,"("]
            code += [self._create_argument_code( indentLevel)]
            code += [')\n']
        return ''.join(code)

    def _create_argument_code(self, indentLevel):
        """_create_argument_code( indentLevel)
   
Creates the list of arguments for a component's init function. This sets all the
items in the component's _attribute_dict, as long as they are different from the
default values. They are formatted to be indented twice beyond indentLevel, with
line breaks between each. To create a single-line argument list, strip out all
'\n' characters.        
"""
        dummy = self.__class__()
        argIndent = _INDENT * (indentLevel + 2)
        code = []
        for attr in self._attribute_dict:
            store = True
            try:
                val = getattr(self, attr)
                dummyval = getattr(dummy, attr)
                if val == dummyval:
                    store = False
            except:
                store = False
            if store:
                code += ['\n',argIndent, attr, '=', repr(val),', ']
        return ''.join(code)
    _codeStorageDict = {
                  'custom_export_func': _create_object_code,
                  'as_class': True,
                  'skip_attributes': ['_component_method_names']
                  }
        
class ComponentList(object):

    def __del__(self):
        self.__components = None
        self.__methods = None

    def __init__(self):
        self.__components = []
        self.__methods = {}

    def add(self, component, **kwargs):
        """add( component, **kwargs)
        
component: must either be a component instance or a component class.
kwargs: will be assigned to component attributes as per component.__init__
"""
        if isinstance(component, Component):
            component.__init__( **kwargs)
        elif issubclass( component, Component):
            component = component( **kwargs)
        else:
            raise TypeError(message=''.join(['ComponentList.add: ',
                                             repr(component), 
                                             "is not a component"]))
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
