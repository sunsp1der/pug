"CallbackObject.py"

from weakref import WeakKeyDictionary

from pug import BaseObject

class CallbackObject(BaseObject):
    """CallbackObject( gname="")
    
This object allows the user to register callbacks for attribute-change 
notification. The syntax is as follows:

callback_object_instance.register_callback( attribute, callback_func)
callback_object_instance.unregister_callback( attribute, callback_func)

callback_func will be called as follows:
    callback_func (value, attribute name, CallbackObject instance) 
"""
    __callbackDict = {}

    def __init__(self, *a, **kw):
        BaseObject.__init__(self, *a, **kw)
        
    def register_callback(self, attr, callbackfunc):
        """register_callback( attr, callbackfunc)
        
attr: the attribute to watch for changes
callbackfunc: the callback function. It will receive:
                            callbackfunc( value, attribute name, this object)
"""
        try:
            self.__callbackDict[attr] += [callbackfunc]
        except:
            self.__callbackDict[attr] = [callbackfunc]
            
    def unregister_callback(self, attr, callbackfunc):
        """unregister_callback( attr, callbackfunc): unregister callbackfunc"""
        try:
            self.__callbackDict[attr].remove(callbackfunc)
        except:
            pass
        
    def clear_callbacks(self):
        for attr, list in self.__callbackDict.iteritems():
            self.__callbackDict[attr] = []
        
    def __setattr__(self, attr, value):
        BaseObject.__setattr__(self, attr, value)
#        try:
        if attr in self.__callbackDict:
            for callback in self.__callbackDict[attr]:
                callback( value, attr, self)
#                try:
#                    callback( value, attr, self)
#                except:
#                    self.__callbackDict[attr].remove(callback)
#        except:
#            pass
        
    def __del__(self):
        # don't know why this try is necessary, but I get an exception without
        # it
        try:
            self.clear_callbacks()
            BaseObject.__del__(self)
        except:
            pass

if __name__ == '__main__':
    from pug import get_gnamed_object

    def pr(*a, **kw):
        print "PR!",a, kw

    obj = CallbackObject("doo")
    print get_gnamed_object("doo")

    obj.register_callback( "x", pr)
    obj.x = 4
    obj.y = 5
    obj.x = "xxx"
    obj.unregister_callback( "x", pr)
    obj.x = "yyy"
    obj.unregister_callback( "x", pr)
    del(obj)
    print get_gnamed_object("doo")
