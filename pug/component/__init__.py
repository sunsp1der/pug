from pug.component.ComponentObject import ComponentObject
from pug.component.component import Component, component_method
from pug.component.manager import register_component

# these are usually all you need to create a component
__all__ = ['Component', 'register_component', 'component_method']