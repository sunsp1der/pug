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
    
def get_gnamed_object(name):
    if _gnameManager.nameDict.has_key(name):
        nameList = _gnameManager.nameDict[name]
        while len(nameList):
            obj = nameList[0]()
            if obj:
                return obj
            else:
                nameList.pop(0)
    return None

class GnamedObject(object):
    """Has a 'gname' property that auto-registers with the gname manager"""
    def __init__(self, gname = ''):
        self.__gname = ''
        # take care of a class with a default gname
        if self.__class__.gname != GnamedObject.gname:
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
    del(ax)
    print get_gnamed_object('test') #should yield None
    