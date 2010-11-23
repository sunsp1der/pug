from inspect import *
from sys import exc_info
import traceback
import types

from pug.constants import *
from pug.util import get_type
from pug.pugview_manager import get_agui_default_dict, get_default_pugview

_DEBUG = False

def create_pugview_aguilist(obj, window, pugview, filterUnderscore = 2):
    """create_pugview_pug(obj, window, pugview, filterUnderscore) -> aguilist 
    
    aguilist is a list of pug aguis for obj
    
obj: object to be examined
window: the pugFrame object  
pugview: pugview to be used.
filterUnderscore: 2 = don't show __attributes, 1 = don't show _attributes either

Create a gui based on pugview. A class' pugview can be created as follows:
pugview  = \
{
    'name': mySpecialView
    # the name of this pugview
    # if this is not defined, 'Pugview #' will be assigned

    'size': (400, 300)
    # the start size of the pug frame, in pixels
    # if this is not defined, default size will be assigned

    'defaults':{  
        'int':[Number,{'decimals':0}]
        # attribute class name:[agui,aguidata (dict is standard)]
    },
    # defaults are used if agui is unspecified in 'attributes'
    # if the default isn't found in this list, uses the create_raw_gui defaults 
    # this is optional

    'attributes':[
        ['<attribute>',<agui> or '<tooltip>',<aguidata>],
        ['gname'], # 'gname' is attribute. use agui from 'defaults'
        ['position',Vector2,{'decimals':3}], # Vector2 is agui
        ['ratio','tooltip blabla'], # 'tooltip blabla' is tooltip. Default agui
        ['notmesswith', None, {'read_only':True}], # use agui from 'defaults'
        ['*']
    ]
    # list of attributes to display. ['*'] = list all remaining using defaults
    # if this is not defined, ['*'] is assumed
    
    'create_pug_list_function': fn 
    # a custom aguilist creation function can be specified here
    # this is optional
    # fn(obj, window, filterUnderscore) will be called 
    # arguments are as per this function
    
    'skip_menus': ['menu_name',...]
    # a list of menus that will NOT be shown in the menubar. Standard menus 
    # include 'View' and 'Export', but more can be added with 
    # app.set_global_menus or manually.
    
    'info_function': fn
    # a custom info function can be specified here
    # this is optional
    # fn( obj, window, objectPath) -> info frame
    # arguments are as per this function. objectPath is a string representing
    # the programatic path to obj. If fn opens a frame, it should return it.
    
    'no_source': bool
    # if True, no 'View source code' option will be shown in View menu
}
import pug
pug.add_pugview(myClass, pugview)

Additionally, an instance or class can have a '_pug_pugview_class' attribute 
which contains the class whose pugviews can be used. For example:

class otherClass( myClass):
    _pug_pugview_class = myClass
"""
    if _DEBUG: print "create_pugview_aguilist: begin"
    if pugview.has_key('create_pug_list_function'):
        aguilist = pugview['create_pug_list_function'](obj, 
                                                       window, filterUnderscore)
    else:
        dirList = dir(obj)
        if pugview.has_key('attributes'):
            attributeList = pugview['attributes']
        else:
            attributeList = [['*']] # show all
        if pugview.has_key('defaults'):
            defaultDict = pugview['defaults']
        else:
            defaultDict = {}
        aguilist = []
        # go through list of attributes in pugview
        if _DEBUG: print obj
        for entry in attributeList:
            attributegui = None
            attribute = entry[0]
            if _DEBUG: print "create_pugview_aguilist: attr -", attribute
            if attribute == '*':
                #create default gui for all attributes we haven't made a gui for
                for attribute in dirList:
                    # test underscores
                    if filterUnderscore:
                        if do_filter_underscore(attribute, filterUnderscore):
                            continue
                    attributegui = create_default_agui(attribute, obj, window)
                    if attributegui:
                        aguilist.append(attributegui)
                continue
            # make sure we have an attribute, or a non-attr agui entry
            if not(attribute) and len(entry) == 1:
                continue
            # TODO: make a warning list viewable in the pugframe for this:
            tooltip = None
            agui = None
            if len(entry) > 1:
                # do we have the agui type or a doc string?
                if type(entry[1]) in types.StringTypes:
                    tooltip = entry[1]
                elif entry[1]:
                    agui = entry[1]
                # do we have special info for the agui?
                if len(entry) > 2:
                    aguidata = entry[2].copy()
                else:
                    aguidata = {}
                if tooltip:
                    aguidata['doc'] = tooltip
            if agui:
                # create the agui
                attributegui = get_agui(agui, 
                                        attribute, window, aguidata=aguidata)
            else:
                # no specified agui, so figure out the default
                try:
                    attributeValue = getattr(obj,attribute)
                except:
                    continue
                if isclass(attributeValue):
                    attributeClass = attributeValue
                else:
                    attributeClass = get_type(attributeValue)
                if defaultDict.has_key(attributeClass):
                    info = defaultDict[attributeClass]
                    agui = info[0]
                    if len(info) > 2:
                        aguidata = info[2].copy()  
                    else:
                        aguidata = {}
                    if tooltip:      
                        aguidata['doc'] = tooltip
                    attributegui = get_agui(agui, attribute, window, 
                                                aguidata=aguidata)
                else:
                    if len(entry) > 2:
                        aguidata = entry[2].copy()
                    else:
                        aguidata = {}
                    if tooltip:      
                        aguidata['doc'] = tooltip
                    attributegui = create_default_agui(attribute, obj, window, 
                                                           aguidata=aguidata)
            if attributegui:
                aguilist.append(attributegui)
            if entry[0] in dirList:
                dirList.remove(entry[0])
    if _DEBUG: print "create_pugview_aguilist: end"
    return aguilist

def create_raw_aguilist(obj, window, familyList = None, filterUnderscore = 2):
    """create_raw_pug(obj, window) -> aguilist (list of pug aguis for obj)
    
obj: object to be examined
window: the pugFrame object  
familyList: a list of acceptable attribute families (see get_attribute_family)
filter_underscore: 0=no filter, 1=filter _ and __ attributes, 2=filter __ attr's

take all the objects attributes and make entries based on defaults defined in:
<guisystem>.attributeguis.__init__
"""
    aguilist = []
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
        agui = None
        try:
            agui = create_default_agui(attribute, obj, window, family)
        except:
            continue
        if agui:
            aguilist.append(agui)
    return aguilist

def do_filter_underscore(attribute, filterUnderscore):
    if (attribute[:1]=='_' and filterUnderscore==1) \
            or (attribute[:2]=='__' and filterUnderscore>=2):
        return True
    else:
        return False
    
def create_default_agui(attribute, obj, window, family = None, aguidata = {}):
    """Create a default attribute gui for a aguilist entry

attribute: the attribute of obj
obj: the object we're making an agui for
window: the parent of the agui
family: see get_attribute_family
aguidata: this dictionary will update the default aguidata dictionary    
"""
    value = getattr(obj, attribute)
    aguiDefaultDict = get_agui_default_dict()
    if isclass(value):
        attributeClass = value
    else:
        attributeClass = get_type(value)
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
    attributegui = get_agui(agui, attribute, window, aguidata=aguidatadefault)
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

def create_aguilist(obj, window, pugview = None):
    """Create the list of attributes for a pug window.

create_pug_list(obj, window, pugview = None)
    obj: object to be examined
    window: the pugFrame object  
    pugview: pugview to be used. None will create a 'Raw' pug window

    
The attributes are returned as a list of attributeGUIs. Generally, attributeGUIs
have a label and a control to go on the left and right of the pug window.
Default attribute guis are defined in <guisystem>.attributeguis.__init__.
For pugview layout, see create_pugview_gui.
"""
# This function is pretty much not used anymore
    if pugview is None:
        pugview = get_default_pugview( obj)
    if pugview is None or not isinstance(pugview, dict):
        # create an unformatted (raw) pug window
        aguilist = create_raw_aguilist(obj, window)
    else:
        aguilist = create_pugview_aguilist(obj, window, pugview)
    return aguilist

def get_agui( cls, attribute, window, aguidata):
    """get_agui(cls, attribute, window, aguidata)->agui instance

cls: agui class
attribute: the attribute to create agui for
window: the pugWindow to display in
aguidata: special info for agui

Get an agui from the cache or create one"""
    agui = None
    if aguiCache.get(cls, None):
        agui = aguiCache[cls].pop()
        try:
            agui.setup( attribute, window, aguidata)
            if _DEBUG: print "   cached agui used:", attribute, agui
        except:
            if _DEBUG: 
                print "#"*80
                print "agui.setup_error", attribute
                print "   agui_type", cls
                print "   ", aguidata
                traceback.print_exc()
                print "#"*80
        else:
            return agui
    try:
        agui = cls( attribute, window, aguidata)
        if _DEBUG: print "agui created:", attribute, agui
    except:
        print "#"*80
        print "agui_creation_error:", attribute, 
        print "   agui_type:", cls
        print "   ", aguidata
        traceback.print_exc()
        print "#"*80
    return agui

# cache aguis here
aguiCache = {} # {agui.__class__: [agui, agui...]}
def cache_agui( agui):
    if aguiCache.get(agui.__class__, False):
        if agui not in aguiCache[agui.__class__]:
            aguiCache[agui.__class__] += [agui]
    else:
        aguiCache[agui.__class__] = [agui]           
