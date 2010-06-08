"""Basic utility functions for pug"""

from __future__ import with_statement
import re
import cPickle
import copy
import sys
import os
import inspect
import subprocess
import signal

from start_file import start_file

_DEBUG = False

_processes = {}
def python_process( python_file, *args, **kwargs):
    """python_process( python_file, *args, **kwargs)
    
Run python_file in a new process
args: string arguments to process
kwargs: flags and options
    close_duplicates: close all processes with same command line. Default=False
"""        
    if os.name == "nt":
        cmd = ["pythonw"]
    else:
        cmd = ["python"]
    cmd += [python_file]
    if args:
        cmd += list(args)
    proc = subprocess.Popen(cmd)
    cmd = ' '.join(cmd)
    if kwargs.get('close_duplicates', False):
        kill_subprocesses(cmd)
    if _processes.has_key(cmd):
        _processes[cmd].append(proc)
    else:
        _processes[cmd] = [proc,]
        
def kill_subprocesses(cmdline=None):
    "kill_subprocess(cmdline): kill all cmdline subprocesses,default: kill ALL"
    if cmdline:
        proclist = _processes.get(cmdline,[])
        for oldproc in proclist:
            if oldproc.poll() is None:
                killcmd = "taskkill /PID " + str(oldproc.pid)
                subprocess.Popen(killcmd)                
    else:
        for cmdline in _processes.iterkeys():
            kill_subprocesses(cmdline)
    
if os.name == "nt":
    _default_editor = "idle.pyw"
else:
    _default_editor = "idle.py" 
_default_editor = os.path.join(os.path.split(sys.executable)[0],
                               'Lib','idlelib',_default_editor)
def edit_process( filename, *args, **kwargs):
    """edit_process( filename, *args, **kwargs)
    
Edit filename in editor
args: arguments to process
kwargs: flags and options
    close_duplicates: close all processes with same command line. Default=True
    editor: path to editor executable. Default=pug.util._default_editor    
"""    
    if kwargs.has_key('editor'):
        editor = kwargs.pop('editor')
    else:
        editor = _default_editor
    if not kwargs.has_key('close_duplicates'):
        kwargs['close_duplicates']=True
    python_process(editor, filename, *args, **kwargs)
    
_IMAGEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Images")
def get_image_path(filename):
    return os.path.join (_IMAGEPATH, filename)

def get_code_file( obj):
    module = inspect.getmodule(obj).__file__
    if module[-3:] == "pyc":
        module = module [:-1]
    return module

def make_valid_attr_name(name):
    name = re.sub(r'^\d*','',name) # remove digits from front
    name = re.sub(r'\W','_',name) # replace non alpha numerics with _
    return name

def prettify_path( path):
    "prettify_path( path)-> normalized path with os separator as divider"
    ret = os.path.normpath(path)
#    ret = ret.replace('\\', os.sep)
#    ret = ret.replace('//', os.sep)
    return ret

def check_name_valid(name):
    validname = make_valid_attr_name(name)
    return name == validname

_cache = {}
_error_cache = {}
    
def get_package_classes(  package='', superClass=object, doReload=False, 
                          folder=None, errors=None):
    """get_package_classes( package, superClass, doReload, folder, errors)> list
    
Find all classes defined in a package. Will search all modules found within the 
given package. Returns a list of those classes.
package='': string of path to package, as in an import statement
superClass=object: only classes that are a subclass of this will be returned
doReload=False: force a reload on any modules found
folder=None: this folder will be added to the sys.path for the search. Note that
    this may create inaccessible __module__ paths in the found classes
errors=None: if a dict is passed in, it will be filled with the results of 
    sys.exc_info() for each module that had a problem being imported. Indexed
    by module
"""
    if type(errors) is not type({}):
        errors = None  
    exception_dict = {}
    if not doReload and _cache.get((package, superClass, folder)):
        if errors is not None:
            exceptions = _error_cache.get((package, superClass, folder))
            errors.update( exceptions)
        return _cache.get((package, superClass, folder))[:]
    if folder and folder not in sys.path:
        sys.path.insert(0, folder)
        remove_folder = True
    else:
        remove_folder = False
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
            errorkey = '.'.join([package, modulename])
            try:
                module = __import__('.'.join([package, modulename]))
            except:
                exception_dict[errorkey] = sys.exc_info()
                continue
            depth = 0
            while depth+1 < len(packagePath):
                module = getattr(module, packagePath[depth+1])
            module = getattr(module, modulename, None)
            if module:
                classList += find_classes_in_module(module, superClass, 
                                                    doReload)
    if errors is not None:
        errors.update(exception_dict)
    if remove_folder:
        sys.path.remove(folder)
    _error_cache[(package, superClass, folder)] = exception_dict
    _cache[(package, superClass, folder)] = classList[:]
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
                    inspect.isclass(obj) and \
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
        simplename = ''.join(["'",gname,"'"])
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

def test_referrers(obj):
    """_test_referrers(obj)
        
Just a debug test to make sure that pug doesn't keep the object alive when it's
supposed to be deleted. This will show all referrers to obj and all referrers 
to those referrers
"""
    print "Referrers to:",obj
    import gc
    gc.collect()
    a = gc.get_referrers(obj)   
    for ob in a:
        print "   ",ob
        b = gc.get_referrers(ob)
        for ob2 in b:
            print "      ", ob2 
        print "_______________________"
    pass