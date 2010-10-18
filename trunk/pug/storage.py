import cPickle
import copy

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

