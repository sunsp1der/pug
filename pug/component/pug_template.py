"""pug_template.py

Template info for components. This file is only used for working with pug guis.
"""

import pug
from pug.puglist import create_template_puglist
from pug.syswx.component_browser import ComponentBrowseFrame

def _create_component_puglist( obj, window, filterUnderscore):
    template = {}
    attributes = []
    template['name'] = 'Standard'
    for attrinfo in obj._attribute_list:
        template_entry = [attrinfo[0]]
        if len(attrinfo) > 1:
            template_entry += [None, {'tooltip':attrinfo[1]}]
        if len(attrinfo) > 2:
            for item, data in attrinfo[2].iteritems():
                if item is 'agui': 
                    template_entry[1] = data
                elif item is 'aguidata':
                    template_entry[2].update(data)
        attributes.append(template_entry)
    attributes.append(['enabled'])
    template['attributes'] = attributes
    pugList = create_template_puglist(obj, window, template, filterUnderscore)
    return pugList

def  _open_component_browser( obj, window, objectPath):
    return ComponentBrowseFrame( window, object=obj.owner, 
                                 start_component=obj.__class__)

_componentTemplate = {
    'name':'Standard View',
    'create_pug_list_function': _create_component_puglist,
    'info_function': _open_component_browser
}
pug.add_template('Component', _componentTemplate, True)
