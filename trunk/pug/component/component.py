from inspect import CO_VARARGS as _CO_VARARGS, \
    CO_VARKEYWORDS as _CO_VARKEYWORDS, getargspec as _getargspec
from new import code as _code, function as _function, \
    instancemethod as _instancemethod
import weakref
from types import MethodType as _MethodType

from pug.code_storage.constants import _INDENT

_DEBUG = False

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
        check to see if an object has a '_component_class_list' attribute, which
        can contain a list of classes that the object is compatible with for
        component usage. If _class_list evaluates to False, all classes are
        considered compatible. This is checked with the utility function
        'is_valid_component_class' 
_attribute_list: List of [[attribute, docstring, {extras}],...]. This is a list 
        of the official attributes of the Component. These are the attributes 
        that will be serialized when the component is saved, and are the 
        attributes that will be shown in pug's default component view. docstring
        can be left out, but it's way better to provide info about attributes.
    {extras}: Extra info about the attribute. Possible values:
        'agui': the pug attribute-gui type to use
        'aguidata': the aguidata to send to the agui
*Other: component attribute defaults should be set at the class level.

@component_method: methods in a component with this decorator are made available
        to the object with this component. Note that component methods stack, so
        that if an object has 2 components with 'on_create' component methods,
        the code 'object.on_create()' will execute BOTH component methods and 
        object's native on_create method if it has one.
        Component methods have loosened argument restrictions as well. If a 
        component method receives arguments that are not declared in the
        function definition, those arguments are ignored rather than creating an
        exception. If a component method expects more arguments than it
        receives, those arguments are automatically set to None.
        Also note that component methods are automatically passed two arguments.
        They receive the 'self' argument like any method AND IN ADDITION they
        receive an 'owner' argument containing the object that the component is
        attached to.
"""    
    _set = None
    _type = None
    _class_list = []
    _attribute_list = []
    _pug_template_class = 'Component'
    __owner = None
    enabled = True
    
    def __init__(self, owner=None, **kwargs):
        self._set_owner(owner)
        for attr, val in kwargs.iteritems():
            setattr(self, attr, val)
            
    def _set_owner(self, owner):
        if self.__owner:
            try:
                self.__owner().component.remove(self)
            except:
                pass
        if owner is not None:
            self.__owner = weakref.ref(owner, self._owner_deleted)
        else:
            self.__owner = None
        
    def get_owner(self):
        if self.__owner is None:
            return None
        else:
            return self.__owner()
            
    def _owner_deleted(self, owner):
        self.enabled = False
        
    owner = property(get_owner, _set_owner, 
                     doc="The object that this component is attached to")
                            
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
items in the component's _attribute_list, as long as they are different from the
default values. They are formatted to be indented twice beyond indentLevel, with
line breaks between each. To create a single-line argument list, strip out all
'\n' characters.
"""
        dummy = self.__class__()
        argIndent = _INDENT * (indentLevel + 2)
        code = []
        attributes = []
        for item in self._attribute_list:
            attributes.append(item[0])
        attributes.append('enabled')
        for attr in attributes:
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
        if _DEBUG: print "ComponentList.add",component,kwargs
        for key in component._component_method_names:
            value = getattr(component, key)
            component_methods = methods.get(key)
            if component_methods is None:
                methods[key] = component_methods = []
            if _DEBUG: print "   methods[",key,']',component_methods
            if _DEBUG: print "       .append:",value
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
        bound_method_ref = cache.get(instance_id)
        if bound_method_ref is None:
            bound_method = _instancemethod(self.__func, instance, cls)

            #def bound_method(*args, **kw_args):
            #    return self.__func(instance, *args, **kw_args)
            cache[instance_id] = weakref.ref(bound_method)
        else:
            bound_method = bound_method_ref()
        return bound_method

    def __init__(self, func):
        self.__doc__ = func.__doc__
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

