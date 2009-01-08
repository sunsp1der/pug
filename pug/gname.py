# gname.py
#
# utilities for giving a global name string to objects
# TODO: func to return the whole list of a given gname
# TODO: make list of gnamed objects weakrefs

from weakref import ref

class _GnameManager(object):
    def __init__(self):
        self.nameDict = {}
    
global _gnameManager 
_gnameManager = _GnameManager()
del _GnameManager

def get_gname_manager():
    return _gnameManager

def set_gname(object, name):
    register_object_gname(object, name)
    # set the object's gname attribute, if possible
    try:
        object.gname = name
    except:
        pass

def register_object_gname(object, name):
    dict = _gnameManager.nameDict
    if hasattr(object,'gname'):
        if get_gnamed_object(name) is object:
            return
        # if we're changing the name, delete the old one from the dict
        if dict.has_key(object.gname):
            for objectref in dict[object.gname]:
                if objectref() is object:
                    dict[object.gname].remove(objectref)
    if not name:
        return
    
    if dict.has_key(name):
        dict[name].insert(0,ref(object))
    else:
        dict[name] = [ref(object),] 
    
def get_gnamed_object(gname):
    """get_gnamed_object( gname) -> object gnamed 'gname'
    
return the object _most recently_ named 'gname'
"""
    if _gnameManager.nameDict.has_key(gname):
        refList = _gnameManager.nameDict[gname]
        while len(refList):
            obj = refList[0]()
            if obj:
                return obj
            else:
                refList.pop(0)
    return None

def get_gnamed_object_list(gname):
    """get_gnamed_object_list( gname) -> list of objects gnamed gname
    
return a list of all objects gnamed 'gname'
"""
    list = []
    if _gnameManager.nameDict.has_key(gname):
        refList = _gnameManager.nameDict[gname]
        removeList = []
        for ref in refList:
            obj = ref()
            if obj:
                list.append(obj)
            else:
                removeList.append(ref)
        for ref in removeList:
            refList.remove(ref)
    return list

def get_gnames(class_list=[]):
    """get_gnames(class_list=[]) -> a list of gnames
    
returns a list of all the managed gnames.

class_list: if provided, only gnamed objects of these classes will be returned
"""
    list = []
    for gname, ref_list in _gnameManager.nameDict.iteritems():
        for ref in ref_list:
            obj = ref()
            if obj:
                if class_list and not isinstance(obj,class_list):
                    continue
                list.append(gname)
                break
    return list

class GnamedObject(object):
    """Has a 'gname' property that auto-registers with the gname manager"""
    def __init__(self, gname = ''):
        self.__gname = ''
        # take care of a class with a default gname
        if hasattr(self.__class__, 'gname') and \
                not isinstance(self.__class__.gname, property):
            gname = self.gname
            self.__class__.gname = GnamedObject.gname
        self.gname = gname
    def __del__(self):
        if _gnameManager:
            self.gname = ''
    def _get_gname(self):
        try:
            return self.__gname
        except:
            return ''    
    def _set_gname(self,value):
        try:
            if self.__gname == value:
                return
        except:
            self.__gname = ''
        register_object_gname(self,value)
        self.__gname = value
    def _del_gname(self):
        if _gnameManager:
            set_gname(self,'')
        try:
            del self.__gname
        except:
            return
    gname = property(_get_gname,_set_gname,_del_gname,
                     "An easily accessed global name for this object")
    
    _codeStorageDict = {
            'skip_attributes': ['__gname']                        
                        }
                    
if __name__ == "__main__":
    ax = GnamedObject('ax')
    print get_gnamed_object('ax') #should yield ax
    ax.gname = 'test'
    print get_gnamed_object('test') #should yield ax
    print get_gnamed_object_list('ax') #should yield empty list 
    print get_gnamed_object_list('test') #should yield list containing ax
    print get_gnames() # should yield ['test']
    print get_gnames((str))
    del(ax)
    print get_gnamed_object('test') #should yield None
    