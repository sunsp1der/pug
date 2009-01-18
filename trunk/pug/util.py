"""Basic utility functions for pug"""

from __future__ import with_statement
import re
import cPickle
import copy
from weakref import WeakKeyDictionary, ref
import sys
import os
import inspect

DEBUG = False

_IMAGEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Images")
def get_image_path(filename):
    return os.path.join (_IMAGEPATH, filename)

def make_name_valid(name):
    name = re.sub(r'^\d*','',name) # remove digits from front
    name = re.sub(r'\W','_',name) # replace non alpha numerics with _
    return name

def check_name_valid(name):
    validname = make_name_valid(name)
    return name == validname
    
def get_package_classes(  package='', superClass=object, doReload=False, 
                          folder=None):
    """get_package_classes( package, superClass, doReload, folder) > list
    
Find all classes defined in a package. Will search all modules found within the 
given package. Returns a list of those classes.
package='': string of path to package, as in an import statement
superClass=object: only classes that are a subclass of this will be returned
doReload=False: force a reload on any modules found
folder=None: this folder will be added to the sys.path for the search. Note that
    this may create inaccessible __module__ paths in the found classes
"""
    if folder and folder not in sys.path:
        sys.path.insert(0, folder)
    classList = []
    packagePath = package.split('.')
    searchFolder = os.path.join(os.getcwd(),*packagePath)
    filelist = os.listdir(searchFolder)
    for filename in filelist:
        # look through files in 'scenes' folder for non-private .py files
        if filename.startswith('_'):
            continue
        modulename, ext = os.path.splitext(filename)
        if ext == '.py':
            # import the .py file
            try:
                module = __import__('.'.join([package, modulename]))
            except:
                continue
            depth = 0
            while depth+1 < len(packagePath):
                module = getattr(module, packagePath[depth+1])
            module = getattr(module, modulename, None)
            if module:
                classList += find_classes_in_module(module, superClass, 
                                                    doReload)
    if folder:
        sys.path.remove(folder)
    return classList

def find_classes_in_module(module, superClass=object, doReload=False):
    """find_classes_in_module(module, superClass=Object)->list of classes
    
return a list of classes from given module. They must all be derived from
superClass
"""
    classList = []
    modulename = module.__name__
    needsReload = modulename in sys.modules
    if doReload and needsReload:
        reload(module)
    items = dir(module)
    for item in items:
        if item.startswith('_'):
            continue
        obj = getattr(module, item)
        if hasattr(obj,'__module__') and \
                obj.__module__ == modulename and \
                issubclass( obj, superClass):
            classList.append(obj)  
    return classList  
            
def get_type(obj):
    if hasattr(obj,'__class__'):
        t = obj.__class__
    else:
        t = type(obj)
    return t                
                     
def get_type_name(obj):
    if inspect.isclass(obj):
        return obj.__name__
    else:
        return get_type(obj).__name__
                                       
def get_simple_name(obj, objectpath='unknown'):
    """analyze_path( obj, objectpath) -> shortpath

obj: an object
objectpath: a programattic path to object.  e.g. 'parent.child.attribute'

Return a simple name for obj.  Not unique or anything... just for a basic label
like pugframe titles...
"""
    gname = getattr(obj,'gname','')
    if gname and type(gname) == str:
        simplename = gname
    elif objectpath == 'unknown':
        simplename = get_type_name(obj)
    else:
        simplename = re.split('\.',objectpath)[-1:][0]           
        if not simplename:
            simplename = objectpath     
    return simplename                

def pugSave(obj, filename):
    "Use some awesomely raunchy hacks to force obj to save as much as it can"""
    # use a dummy to avoid changing original
    dummy = copy.copy(obj)
    
    # awesomely raunchy hack below
    # pugXDict contains information not normally accessible via __dict__
    dummy._pugXDict = _create_pugXDict(dummy)
    
    if hasattr(obj, '__getstate__'):
        # use getstate to allow customization ala pickle and copy
        dummyDict = obj.__getstate__()
    else:
        dummyDict = dummy.__dict__
    
    # remove unpickleable items from dummy
    for label, item in obj.__dict__.iteritems():
        try:
            s = cPickle.dumps(item)
        except:
            del dummyDict[label]

    savefile = open(filename, 'wb')
    cPickle.dump(dummy, savefile)
    
def pugLoad(obj, filename):
    """Decode pugSave's awesomely raunchy hackery"""
    loadfile = open(filename, 'rb')
    # use a dummy so we can just use its dict
    dummy = cPickle.load(loadfile)
    dummyDict = dummy.__dict__
    if hasattr(obj, '__setstate__'):
        # use setstate to allow customization ala pickle and copy
        obj.__setstate__(dummyDict)
        pugXDict = dummyDict.pop('_pugXDict', {})
    else:
        pugXDict = dummyDict.pop('_pugXDict', {})
        obj.__dict__.update(dummyDict)
        
    # load the pugXDict that hacks in dir() attributes that might not show up
    # in __dict__
    _update_pugXDict(obj, pugXDict)

# I COULD make this recursive and accept a depth value.  Therein lie dragons
def _create_pugXDict(dummy):
    """create pugXDict, which contains all pickleable values in dir(dummy)
this is a bit hacky, but can store some things that a straight pickle can't
"""
    
    pugXDict = {}
    dummyDir = dir(dummy)
    dummyDict = dummy.__dict__
    # store most pickleable items in dummyDir
    for attribute in dummyDir:
        #don't get into object's private business
        if attribute[0]=='_':
            continue
        try:
            value = getattr(dummy, attribute)
            # no wasting time on funcs. 
            if callable(value):
                continue
            s = cPickle.dumps(value)
        except:
            # hack downward one more level
            subObject = value
            subDir = dir(subObject)
            subDict = {}
            for subAttribute in subDir:
                # no private sub-attributes either
                if subAttribute[0] =='_':
                    continue
                try:
                    subValue = getattr(subObject,subAttribute)
                    s = cPickle.dumps(subValue)
                except:
                    continue
                subDict[subAttribute] = subValue
            # prefix hardcore attributes with a 0
            if not subDict:
                continue
            attribute = ''.join(['0',attribute])
            value = subDict
        else:
            #no need to get anything that's in the dummyDict AND pickleable 
            if attribute in dummyDict:
                continue            
        pugXDict[attribute] = value
    return pugXDict
    
def _update_pugXDict(obj, pugXDict):    
    """Hack a pugXDict into obj. See _create_pugXDict for the gorey details"""
    for attribute in pugXDict:
        if attribute[0] == '0':
            subDict = pugXDict[attribute]
            attribute = attribute[1:]
            subObject = getattr(obj,attribute)
            for subAttribute in subDict:
                subValue = subDict[subAttribute]
                try: 
                    setattr(subObject,subAttribute,subValue)
                except:
                    continue
        else:
            try:
                setattr(obj,attribute,pugXDict[attribute])
            except:
                continue

class CallbackWeakKeyDictionary(WeakKeyDictionary):
    """A WeakKeyDictionary that sends callbacks when the dictionary changes

CallbackWeakKeyDictionary(dict=None) -> CallbackWeakKeyDictionary instance
dict: a dictionary to be converted
"""
    def register(self, func):
        """register( func)
        
register to receive a callback whenever an operation is performed on the dict
WARNING: You must unregister when you don't want a callback anymore! A reference
    is stored!
Whenever there is a change, all registered callables will receive:
    callable( dict, func_name, arg1, arg2)
        dict: the CallbackWeakKeyDictionary instance
        func_name: the name of the function causing the change.  
        arguments can be None if not applicable... usually arg1=key, arg2=value
"""
        if not callable(func):
            raise TypeError(''.join(['register() arg1 not callable:', 
                                     str(func)]))
        self.callbacks.add(func)

    def register_for_delete(self, func):
        """register_for_delete( func)
        
register to receive a callback when a dict key is deleted. This includes when
the object refered to by the weak key is deleted.
WARNING: You must unregister when you don't want a callback anymore! A reference
    is stored!
Whenever a key is deleted, all registered callables will receive:
    callable( dict, func_name, key, value)
        dict: the CallbackWeakKeyDictionary instance
        func_name: the name of the function causing the change. For deletes,
            this can be '_remove', '__delitem__', 'pop', 'popitem'
        key: the dict key
        value: the dict value
"""
        if not callable(func):
            raise TypeError(''.join(['register_for_delete() arg1 not callable:',
                                     str(func)]))
        self.deleteCallbacks.add(func)
        
    def unregister(self, func):
        """unregister (func)
        
remove func from callback and deleteCallback registries"""
        if func in self.callbacks:
            self.callbacks.remove(func)
        if func in self.deleteCallbacks:
            self.deleteCallbacks.remove(func)
        
    def doCallbacks(self, funcname, arg1, arg2):
        for callback in self.callbacks:
            callback( self, funcname, arg1, arg2)
        for callback in self.deleteCallbacks:
            if funcname in ['_remove', '__delitem__', 'pop', 'popitem']:
                callback( self, funcname, arg1, arg2)

    def __init__(self, dict=None):
        self.data = {}
        self.callbacks = set()
        self.deleteCallbacks = set()
        def remove(k, selfref=ref(self)):
            self = selfref()
            if self is not None:
                value = self.data[k]
                self.doCallbacks('_remove', k, value)
                del self.data[k]
        self._remove = remove
        if dict is not None: self.update(dict)
            
    def __setitem__(self, key, value):
        #og_v = self.data.get(ref(key),not value)
        WeakKeyDictionary.__setitem__(self, key, value)
        #if og_v is not value:
        self.doCallbacks('__setitem__', key, value)
        
    def __delitem__(self, key):
        value = self[key]
        WeakKeyDictionary.__delitem__(self, key)
        self.doCallbacks('__delitem__', key, value)
        
    def pop(self, key):
        value = WeakKeyDictionary.pop(self, key)
        self.doCallbacks('pop', key, value)        
        return value
    
    def popitem(self):
        key, value = WeakKeyDictionary.popitem( self)
        self.doCallbacks('popitem', key, value)        
        return key, value
        
    def clear(self):
        WeakKeyDictionary.clear( self)
        self.doCallbacks('clear', None, None)        
        
    def update(self, dict=None, **kwargs):
        WeakKeyDictionary.update( self, dict, kwargs)
        self.doCallbacks('update', dict, kwargs)
        
    def setdefault(self, key, default=None):
        #og_v = self.data[ref(key)]
        v = WeakKeyDictionary.setdefault(key, default)
        #if v is not og_v:
        self.doCallbacks('setdefault', key, default)
        
    def copy(self):
        new = CallbackWeakKeyDictionary()
        for key, value in self.data.items():
            o = key()
            if o is not None:
                new[o] = value
        return new        
