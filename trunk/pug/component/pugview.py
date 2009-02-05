"""pugview.py

Pugview info for components. This file is only used for working with pug guis.
"""

import pug
from pug.util import test_referrers
from pug.component import Component, component_method
from pug.aguilist import create_pugview_aguilist
from pug.syswx.component_browser import ComponentBrowseFrame

_DEBUG = False

def _create_component_attribute_list( obj):
    attributes = []
    for attrinfo in obj._field_list:
        attributes.append(attrinfo)
    attributes.append(['enabled'])
    if _DEBUG: attributes.append(['test_referrers',pug.Routine,
                                  {'routine':test_referrers}])
    return attributes
    
def _create_field_aguilist( obj, window, filterUnderscore):
    pugview = {}
    attributes = []
    pugview['name'] = 'Component Fields'
    attributes = []
    attributes.append(['Fields',pug.Label])
    attributes += _create_component_attribute_list( obj)
    pugview['attributes'] = attributes
    aguilist = create_pugview_aguilist(obj, window, pugview, filterUnderscore)
    return aguilist

def _create_fieldmethod_aguilist( obj, window, filterUnderscore):
    pugview = {}
    attributes = []
    pugview['name'] = 'Component Fields and Methods'
    attributes.append(['Fields',pug.Label])
    attributes += _create_component_attribute_list( obj)
    attributes.append(['Methods',pug.Label])
    for attr in dir(obj.__class__):
        if isinstance(getattr(obj.__class__, attr), component_method):
            attributes.append([attr])
    pugview['attributes'] = attributes
    aguilist = create_pugview_aguilist(obj, window, pugview, filterUnderscore)
    return aguilist

def  _open_component_browser( obj, window, objectPath):
    return ComponentBrowseFrame( window, object=obj.owner, 
                                 start_component=obj.__class__)

_dataPugview = {
    'name':'Component Fields',
    'create_pug_list_function': _create_field_aguilist,
    'info_function': _open_component_browser
}

_dataMethodPugview = {
    'name':'Component Fields and Methods',
    'create_pug_list_function': _create_fieldmethod_aguilist,
    'info_function': _open_component_browser
}
pug.add_pugview('Component', _dataPugview, True)
pug.add_pugview('Component', _dataMethodPugview, False)
