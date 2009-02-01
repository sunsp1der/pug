"""pugview.py

Pugview info for components. This file is only used for working with pug guis.
"""

import pug
from pug.component import Component, component_method
from pug.aguilist import create_pugview_aguilist
from pug.syswx.component_browser import ComponentBrowseFrame

def _create_component_attribute_list( obj):
    attributes = []
    for attrinfo in obj._attribute_list:
        pugview_entry = [attrinfo[0]]
        if len(attrinfo) > 1:
            pugview_entry += [None, {'tooltip':attrinfo[1]}]
        if len(attrinfo) > 2:
            for item, data in attrinfo[2].iteritems():
                if item is 'agui': 
                    pugview_entry[1] = data
                elif item is 'aguidata':
                    pugview_entry[2].update(data)
        attributes.append(pugview_entry)
    attributes.append(['enabled'])
    return attributes
    
def _create_data_aguilist( obj, window, filterUnderscore):
    pugview = {}
    attributes = []
    pugview['name'] = 'Component Data'
    attributes = _create_component_attribute_list( obj)
    pugview['attributes'] = attributes
    aguilist = create_pugview_aguilist(obj, window, pugview, filterUnderscore)
    return aguilist

def _create_datamethod_aguilist( obj, window, filterUnderscore):
    pugview = {}
    attributes = []
    pugview['name'] = 'Component Data and Methods'
    attributes.append(['Data',pug.Label])
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
    'name':'Component Data',
    'create_pug_list_function': _create_data_aguilist,
    'info_function': _open_component_browser
}

_dataMethodPugview = {
    'name':'Component Data and Methods',
    'create_pug_list_function': _create_datamethod_aguilist,
    'info_function': _open_component_browser
}
pug.add_pugview('Component', _dataPugview, True)
pug.add_pugview('Component', _dataMethodPugview, False)
