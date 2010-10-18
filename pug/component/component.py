from inspect import CO_VARARGS as _CO_VARARGS, \
    CO_VARKEYWORDS as _CO_VARKEYWORDS, getargspec as _getargspec
from new import code as _code, function as _function, \
    instancemethod as _instancemethod
import weakref
from types import StringTypes as _StringTypes
from types import MethodType as _MethodType

from pug.code_storage.constants import _INDENT, _STORE_UNICODE, _PRETTIFY_FLOATS
from pug.util import prettify_data

_DEBUG = False

class Component(object):
    """Component( **kwargs)
    
Pug uses components to add python code to objects at runtime

kwargs: Component.__init__ will assign kwargs as attributes. For example...
MyComponent( size=10, name='biggy') 
When MyComponent is created, its 'size' attribute will be created with value 10
and its 'name' attribute will be created with value 'biggy'
    
    
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
_field_list: List of [attribute, docstring] or [attribute, agui, {aguidata}] 
        This is a list of the official attributes of the Component. These are 
        the attributes that will be saved when the component is saved, and are 
        the attributes that will be shown in pug's default component view. 
        docstring can be left out, but it's way better to provide info about 
        attributes. If agui is provided, the docstring should be in the 'doc'
        dictionary entry. See the docs for aguilist and the various aguis for
        more information.
enabled: When this is false, the component's component_methods will not
    intercept calls to its owner's methods. Calls directly to component_methods 
    will continue to work unless they are explicitly coded not to.
*Other: component attribute defaults should be set at the class level.

@component_method: methods in a component with this decorator are made available
        to the object with this component. Note that component methods stack, so
        that if an object has 2 components with 'on_create' component methods,
        the code 'object.on_create()' will execute both component methods, then 
        the object's native on_create method if it has one.
"""    
    _set = None
    _type = None
    _class_list = []
    _field_list = []
    _component_method_names = None
    _pug_pugview_class = 'Component'
    __owner = None
    enabled = True
    
    def __init__(self, owner=None, **kwargs):
        if owner:
            self.owner = owner
        for attr, val in kwargs.iteritems():
            setattr(self, attr, val)
        cls = self.__class__
        if cls._component_method_names is None:
            cls._setup_method_names()
            
    def _setup_method_names(cls):
        names = []
        for attr in dir(cls):
            if isinstance(getattr(cls,attr), ComponentMethod):
                names.append(attr)
        cls._component_method_names = names
    _setup_method_names = classmethod(_setup_method_names)        
            
    def _set_owner(self, owner):
#        print self.__class__, owner
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
        if _DEBUG: print "component._owner_deleted", self, owner
        self.enabled = False
#        self.owner = None
        
    owner = property(get_owner, _set_owner, 
                     doc="The object that this component is attached to")
                            
#    def _component_method_names(doc):
#        """Returns a generator of component method names."""
#        def get_component_method_names(self):
#            cls = self.__class__
#            return (k for k in dir(cls) \
#                    if isinstance(getattr(cls, k), ComponentMethod))
#        return property(get_component_method_names, doc=doc)
#    _component_method_names = \
#        _component_method_names(_component_method_names.__doc__)
		
    def is_duplicate_of(self, other):
        duplicate = False
        if self.__class__ == other.__class__:
            duplicate = True
            for attrinfo in self._field_list:
                attr = attrinfo[0]
                if getattr(self, attr) != getattr(other, attr):
                    duplicate = False
                    break
        return duplicate         
    
    def on_added_to_object(self):
        """Stub for callback when this component is added to an object"""
        pass
        
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
items in the component's _field_list, as long as they are different from the
default values. They are formatted to be indented twice beyond indentLevel, with
line breaks between each. To create a single-line argument list, strip out all
'\n' characters.
"""
        dummy = self.__class__()
        argIndent = _INDENT * (indentLevel + 2)
        attributes = []
        for item in self._field_list:
            attributes.append(item[0])
        attributes.append('enabled')
        attribute_code = []
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
                output = prettify_data( val)
                attribute_code += [''.join([attr, '=', output])]
        joiner = ''.join([',\n',argIndent])
        code = joiner.join(attribute_code)
        if attribute_code:
            code = ''.join(['\n',argIndent,code])
        else:
            code = ''
        return code
    _codeStorageDict = {
                  'custom_export_func': _create_object_code,
                  'as_class': True,
                  'skip_attributes': ['_component_method_names']
                  }
    def _debug_referrents(self):
        import gc
        gc.collect()
        print "referrers to", self
        g = gc.get_referrers(self)
        for ob in g:
            print "   ",ob
            b = gc.get_referrers(ob)
            for ob2 in b:
                print "      ",ob2
        
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
        methods = self.__methods
#        if _DEBUG: print "ComponentList.add",component,kwargs
        for key in component._component_method_names:
            value = getattr(component, key)
            component_methods = methods.get(key)
            if component_methods is None:
                methods[key] = component_methods = []
#            if _DEBUG: print "   methods[",key,']',component_methods
#            if _DEBUG: print "       .append:",value
            component_methods.append(value)
        self.__components.append(component)

    def get_components(self):
        return self.__components

    def get_methods(self, key):
        return self.__methods.get(key)

    def get_method_names(self):
        return self.__methods.keys()

    def remove(self, component):
        methods = self.__methods
        for key in component._component_method_names:
            value = getattr(component, key)
            methods_list = methods[key]
            methods_list.remove(value)
            if not len(methods_list):
                del methods[key]
        self.__components.remove(component)
        component.owner = None
  
class ComponentMethod(object):
        
    def __del__(self):
        self.__cache = None
        self.__func = None
        
    def __call__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        cache = self.__cache
        instance_id = id(instance)
        bound_method_ref = cache.get(instance_id)
        if bound_method_ref is None or bound_method_ref() is None:
            bound_method = _instancemethod(self.__func, instance, cls)
            cache[instance_id] = weakref.ref(bound_method)
        else:
            bound_method = bound_method_ref()
#        if _DEBUG: print "ComponentMethod.__get__:",instance, cls, bound_method
        return bound_method
    
    def __init__(self, func):
        self.__doc__ = func.__doc__
        code = func.func_code
        flags = code.co_flags
        locals = code.co_nlocals
        n = code.co_argcount
        names = list(code.co_varnames)
        has_args = has_kwargs = True
        if not (flags & _CO_VARKEYWORDS):
#            flags |= _CO_VARKEYWORDS
#            locals += 1
#            names.insert(n, '___fake_kwargs')
            has_kwargs = False
        if not (flags & _CO_VARARGS):
#            flags |= _CO_VARARGS
#            locals += 1
#            names.insert(n, '___fake_args')
            has_args = False
        new_code = _code(n, locals, code.co_stacksize, flags, code.co_code,
                         code.co_consts, code.co_names, tuple(names),
                         code.co_filename, code.co_name, code.co_firstlineno,
                         code.co_lnotab)
        self.__cache = {}
        self.__func = _function(new_code, func.func_globals, func.func_name,
                                func.func_defaults, func.func_closure)
#        self.__func.__fake_args = fake_args
#        self.__func.__fake_kwargs = fake_kwargs
        argspec = _getargspec(self.__func)
#        args, varargs, varkw, defaults = argspec
        if has_args:
            self.__func.__maxargs = 666
        else:
            self.__func.__maxargs = len(argspec[0]) -1
        if argspec[3] == None:
            defaults = []
            defaultlen = 0
        else:
            defaults = argspec[3]
            defaultlen = len(argspec[3]) 
        self.__func.__minargs = len(argspec[0]) - defaultlen - 1
        self.__func.__args = argspec[0]
        self.__func.__defaults = defaults
        self.__func.__has_args = has_args
        self.__func.__has_kwargs = has_kwargs

component_method = ComponentMethod

