"""Basic utility functions for pug"""

from __future__ import with_statement
import re
import cPickle
import copy
from weakref import WeakKeyDictionary, ref
import sys
import os

PUGIMAGEPATH = os.path.join(os.path.dirname(__file__),"Images")
def imagePath(file):
    return os.path.join (PUGIMAGEPATH,file)

def get_folder_classes( folder=None, superClass=object, doReload=False):
    """get_folder_classes( folder=None, objectClass=object, doReload=False)>list
    
Find all classes defined in a folder. Return a list of those classes.
folder: what folder to look in
superClass: only classes that are a subclass of this will be returned
doReload: force a reload on any modules found
"""
    if folder not in sys.path:
        sys.path.insert(0, folder)
    classList = []
    filelist = os.listdir(folder)
    for filename in filelist:
        # look through files in 'scenes' folder for non-private .py files
        if filename.startswith('_'):
            continue
        modulename, ext = os.path.splitext(filename)
        if ext == '.py':
            # import the .py file
            try:
                needsReload = modulename in sys.modules
                module = __import__(modulename)
            except:
                continue
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
                                       
def get_simple_name(obj, objectpath='unknown'):
    """analyze_path( obj, objectpath) -> shortpath

obj: an object
objectpath: a programattic path to object.  e.g. 'parent.child.attribute'

Return a simple name for obj.  Not unique or anything... just for a basic label
like pugframe titles...
"""
    gname = getattr(obj,'gname','')
    if gname:
        simplename = gname
    elif objectpath == 'unknown':
        simplename = obj.__class__.__name__
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

To register for a callback: 
    CallbackWeakKeyDictionaryInstance.register( callable)
To unregister for a callback:
    CallbackWeakKeyDictionaryInstance.unregister( callable)
WARNING: You must unregister when you don't want a callback anymore! A reference
    is stored!
Whenever there is a change, all registered callables will receive:
    callable( dict, func_name, arg1, arg2)
        dict is the CallbackWeakKeyDictionary instance
        func_name is the name of the function causing the change.  
        arguments can be None if not applicable
"""
    def register(self, func):
        if not callable(func):
            raise TypeError(''.join(['register() arg1 not callable:', 
                                     str(func)]))
        self.callbacks.add(func)
        
    def unregister(self, func):
        self.callbacks.remove(func)
        
    def doCallbacks(self, funcname, arg1, arg2):
        for func in self.callbacks:
            func( self, funcname, arg1, arg2)

    def __init__(self, dict=None):
        self.data = {}
        self.callbacks = set()
        def remove(k, selfref=ref(self)):
            self = selfref()
            if self is not None:
                self.doCallbacks('_remove',k,None)
                del self.data[k]
        self._remove = remove
        if dict is not None: self.update(dict)
            
    def __setitem__(self, key, item):
        og_v = self.data.get(ref(key),not item)
        WeakKeyDictionary.__setitem__(self, key, item)
        if og_v is not item:
            self.doCallbacks('__setitem__', key, item)
        
    def __delitem__(self, key):
        WeakKeyDictionary.__delitem__(self, key)
        self.doCallbacks('__delitem__', key, None)
        
    def pop(self, key):
        p = WeakKeyDictionary.pop(self, key)
        self.doCallbacks('pop', key, None)        
        return p
    
    def popitem(self):
        o,value = WeakKeyDictionary.popitem( self)
        self.doCallbacks('popitem', None, None)        
        return o, value
        
    def clear(self):
        WeakKeyDictionary.clear( self)
        self.doCallbacks('clear', None, None)        
        
    def update(self, dict=None, **kwargs):
        WeakKeyDictionary.update( self, dict, kwargs)
        self.doCallbacks('update', dict, kwargs)
        
    def setdefault(self, key, default=None):
        og_v = self.data[ref(key)]
        v = WeakKeyDictionary.setdefault(key, default)
        if v is not og_v:
            self.doCallbacks('setdefault', key, default)
        
    def copy(self):
        new = CallbackWeakKeyDictionary()
        for key, value in self.data.items():
            o = key()
            if o is not None:
                new[o] = value
        return new        