from inspect import *
from sys import exc_info

from pug.constants import *
from pug.templatemanager import get_agui_default_dict

def create_template_puglist(obj, window, template, filterUnderscore = 2):
    """create_template_pug(obj, window) -> pugList (list of pug aguis for obj)
    
obj: object to be examined
window: the pugFrame object  
template: template to be used.

Create a gui based on template. A class' template can be created as follows:
pugTemplate  = \
{
    # the name of this template
    # if this is not defined, 'Template #' will be assigned
    'name': mySpecialView

    # the start size of the pug frame, in pixels
    # if this is not defined, default size will be assigned
    'size': (400, 300)

    # defaults are used if agui is unspecified in 'attributes'
    # if the default isn't found in this list, uses the create_raw_gui defaults 
    # this is optional
    'defaults':{  
        'int':[Number,{'decimals':0}]
        # attribute class name:[agui,aguidata (dict is standard)]
    },

    # list of attributes to display. ['*'] = list all remaining using defaults
    # if this is not defined, ['*'] is assumed
    'attributes':[
        ['<attribute>',<agui>,<aguidata>],
        ['gname'], # use agui from 'defaults'
        ['position',Vector2,{'decimals':3}],
        ['notmesswith', None, {'read_only':True}], # use agui from 'defaults'
        ['*']
    ]
    
    # a custom puglist creation function can be specified here
    # this is optional
    'create_pug_list_function': fn # fn(obj, window) will be called
}
import pug
pug.add_template(myClass, pugTemplate)

Additionally, an instance or class can have a '_pugTemplateClass' attribute 
which contains the class whose templates can be used. For example:

class otherClass( myClass):
    _pugTemplateClass = myClass
"""
    if template.has_key('create_pug_list_function'):
        pugList = template['create_pug_list_function'](obj, window)
    else:
        dirList = dir(obj)
        if template.has_key('attributes'):
            attributeList = template['attributes']
        else:
            attributeList = [['*']] # show all
        if template.has_key('defaults'):
            defaultDict = template['defaults']
        else:
            defaultDict = {}
        pugList = []
        # go through list of attributes in template
        for entry in attributeList:
            attribute = entry[0]
            if attribute == '*':
                #create default gui for all attributes we haven't made a gui for
                for attribute in dirList:
                    # test underscores
                    if filterUnderscore:
                        if do_filter_underscore(attribute, filterUnderscore):
                            continue
                    try:
                        attributegui = create_default_agui(attribute, obj, 
                                                           window)
                    except:
                        continue
                    pugList.append(attributegui)
                continue
            # make sure we have an attribute, or a non-attr agui entry
            if not(attribute) and len(entry) == 1:
                continue
            # TODO: make a warning list viewable in the pugframe for this:
#            if attribute and attribute not in dirList:
#                continue
            # do we have a specified agui?
            if len(entry) > 1 and entry[1]:
                agui = entry[1]
                # do we have special info for the agui?
                if len(entry) > 2:
                    aguidata = entry[2]
                else:
                    aguidata = {}
                # create the agui
                attributegui = agui(attribute, window, aguidata = aguidata)
            else:
                # no specified agui, so figure out the default
                try:
                    attributeValue = getattr(obj,attribute)
                except:
                    continue
                attributeClass = attributeValue.__class__
                if defaultDict.has_key(attributeClass):
                    info = defaultDict[attributeClass]
                    agui = info[0]
                    if len(info) > 2:
                        aguidata = info[2]
                    try:
                        attributegui = agui(attribute, window, 
                                            aguidata = aguidata)
                    except:
                        continue
                else:
                    if len(entry) > 2:
                        aguidata = entry[2]
                    else:
                        aguidata = {}
                    try:
                        attributegui = create_default_agui(attribute, obj, 
                                                           window, 
                                                           aguidata=aguidata)
                    except:
                        continue       
            pugList.append(attributegui)
            if entry[0] in dirList:
                dirList.remove(entry[0])
    return pugList

def create_raw_puglist(obj, window, familyList = None, filterUnderscore = 2):
    """create_raw_pug(obj, window) -> pugList (list of pug aguis for obj)
    
obj: object to be examined
window: the pugFrame object  
familyList: a list of acceptable attribute families (see get_attribute_family)
filter_underscore: 0=no filter, 1=filter _ and __ attributes, 2=filter __ attr's

take all the objects attributes and make entries based on defaults defined in:
<guisystem>.attributeguis.__init__
"""
    pugList = []
    dirList = dir(obj) # the object's attributes
    for attribute in dirList:
        # test underscores
        if filterUnderscore:
            if do_filter_underscore(attribute, filterUnderscore):
                continue
        # test family
        if familyList:
            try:
                family = get_attribute_family(obj, attribute)
            except:
                continue
            if family not in familyList:
                continue
        else:
            family = None
        # create agui
        try:
            agui = create_default_agui(attribute, obj, window, family)
        except:
            error = exc_info()
            continue
        pugList.append(agui)
    return pugList

def do_filter_underscore(attribute, filterUnderscore):
    if (attribute[:1]=='_' and filterUnderscore==1) \
            or (attribute[:2]=='__' and filterUnderscore>=2):
        return True
    else:
        return False
    
def create_default_agui(attribute, obj, window, family = None, aguidata = {}):
    """Create a default attribute gui for a puglist entry

attribute: the attribute of obj
obj: the object we're making an agui for
window: the parent of the agui
family: see get_attribute_family
aguidata: this dictionary will update the default aguidata dictionary    
"""
    value = getattr(obj, attribute)
    aguiDefaultDict = get_agui_default_dict()
    attributeClass = value.__class__
    if aguiDefaultDict.has_key(attributeClass):
        guiType = attributeClass
    else:
        if not family:
            # figure out what gui to use
            family = get_attribute_family(obj, attribute)
        guiType = family
    
    agui = aguiDefaultDict[guiType][0]
    if len(aguiDefaultDict[guiType]) > 1:
        aguidatadefault = aguiDefaultDict[guiType][1]
    else:
        aguidatadefault = {}    
    aguidatadefault.update(aguidata)
    attributegui = agui(attribute, window, aguidata = aguidatadefault)
    return attributegui

def get_attribute_family(obj, attribute):
    """get_attribute_family(obj, attribute) -> attribute family

Returns a string: 
    'Default' for basic python types
    'Routine' for callables
    'Objects' for anything else
"""

    value = getattr(obj,attribute)
    guiType = 'Default'
    if type(value) in BASIC_TYPES:
        guiType = 'Default'
    elif isroutine(value):
        guiType = 'Routine'
    else:
    # if we don't have a type, we'll just let the user open a pug for it
        guiType = 'Objects'
    return guiType

def create_puglist(obj, window, template = None):
    """Create the list of attributes for a pug window.

create_pug_list(obj, window, template = None)
    obj: object to be examined
    window: the pugFrame object  
    template: template to be used. None will create a 'Raw' pug window

    
The attributes are returned as a list of attributeGUIs. Generally, attributeGUIs
have a label and a control to go on the left and right of the pug window.
Default attribute guis are defined in <guisystem>.attributeguis.__init__.
For template layout, see create_template_gui.
"""
# This function is pretty much not used anymore
    if template is None:
        # create an unformatted (raw) pug window
        pugList = create_raw_puglist(obj, window)
    else:
        pugList = create_template_puglist(obj, window, template)
    return pugList

