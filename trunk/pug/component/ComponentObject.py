from weakref import ref as _ref

from pug.component.component import *

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

           Adds component to the object.  'component' can be a component class
           OR instance.  If it's a class, an instance will be created and
           added."""

        if not isinstance(component, Component):
            try:
                is_component_class = issubclass(component, Component)
            except TypeError:
                is_component_class = False
            if not is_component_class:
                raise TypeError("invalid argument")
            component = component()
        component_list = self.__component_list
        component_list.add(component)
        obj = self.__obj()
        original_methods = self.__original_methods
        sentinel = self.__sentinel
        for name in component._component_method_names:
            component_methods = list(component_list.get_methods(name))
            original_method = original_methods.get(name, sentinel)
            if original_method is sentinel:
                original_method = getattr(obj, name, None)
                original_methods[name] = original_method

            def component_wrapper(*args, **kw_args):
                for method in component_methods:
                    method(obj, *args, **kw_args)
                original_method = self.__original_methods[name]
                if original_method is not None:
                    return original_method(*args, **kw_args)

            component_wrapper.__doc__ = original_method.__doc__
            setattr(obj, name, component_wrapper)
        return component

    def get(self, cls=None):
        components = self.__component_list.get_components()
        if cls is None:
            return components
        return (b for b in components if isinstance(b, cls))

    def get_one(self, cls):
        for b in self.get(cls):
            return b

    def remove(self, component):
        component_list = self.__component_list
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