"CallbackWeakKeyDictionary.py"

from weakref import WeakKeyDictionary, ref

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
        for callback in list(self.callbacks):
            callback( self, funcname, arg1, arg2)
        for callback in list(self.deleteCallbacks):
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