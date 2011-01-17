"""Basic utility functions for pug"""

from __future__ import with_statement
import re
import sys
import os
import inspect
import subprocess

from start_file import start_file

_DEBUG = False

_processes = {}
def python_process( python_file, *args, **kwargs):
    """python_process( python_file, *args, **kwargs)
    
Run python_file in a new process
args: string arguments to process
kwargs: flags and options
    close_duplicates: close all processes with same command line. Default=False
    no_record: don't keep a record of this for kill_subprocesses. Default=False
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
    if not kwargs.get('no_record', False):
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
                try:
                    subprocess.Popen(killcmd)
                except:
                    pass                
    else:
        for cmdline in _processes.iterkeys():
            kill_subprocesses(cmdline)
    
if os.name == "nt":
    _default_editor = "idle.pyw"
else:
    _default_editor = "idle.py" 
_default_editor = os.path.join(os.path.split(sys.executable)[0],
                               'Lib','idlelib',_default_editor)
def start_edit_process( filename, *args, **kwargs):
    """start_edit_process( filename, *args, **kwargs)
    
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

def sort_case_insensitive( lst):
    def lower_if_possible(x):
        try:
            return x.lower()
        except AttributeError:
            return x  
    lst.sort(  key=lambda x: map(lower_if_possible, x))          
    

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

def prettify_float( val, precision=3):
    """prettify_float(val, precision=3)->prettified string
    
This function rounds floating point numbers and returns a string. Precision is
the number of digits in a row that have to be either 0 or 9 in order to round.
For example, if precision is 3, 5.0100004 returns 5.01 and 3.99999942412 returns
4.0
"""
    s = str(val)
    point = s.find('.')
    if point == -1:
        return s
    down = s.find('0'*precision,point)
    up = s.find('9'*precision, point)
    if (down < up or up == -1) and down != -1:
        s = s[:down]
        if s[down-1] == '.':
            s += '0'
        return s
    elif up != -1:
        s = s[:up]
        if s[up-1] == '.':
            s = s[:-3] + str(int(s[up-2])+1) + '.0'
        else:
            s = s[:-1] + str(int(s[up-1])+1)
        return s
    return s
     
def prettify_data( val, precision=3):
    """prettify_data( val, precision=3)->prettified string
    
Prettify various data including floats, -0.0 etc."""   
    from pug.code_storage.constants import _STORE_UNICODE, _PRETTIFY_FLOATS  
    if not _STORE_UNICODE and val is unicode(val):
        # we convert unicode values to strings just for pretty's sake
        val = str(val)
    if repr(val) == '-0.0': 
        # I don't totally understand why negative zero is possible
        val = 0.0 
    if _PRETTIFY_FLOATS and (type(val) == list or type(val) == tuple):
        # prettify floats in lists and tuples
        if type(val) == list:
            output = "["
            end = "]"
        else:
            output = "("
            end = ")"
        items = []
        for item in val:
            if type(item) == float:
                items.append( prettify_float(item, precision))
            else:
                items.append( repr(item))
        output += ", ".join(items) + end
    elif _PRETTIFY_FLOATS and type(val) == float:
        # prettify floats
        output = prettify_float(val, precision)
    elif type(val) != str and type(val) != unicode:
        output = repr(val)
    else:
        output = val
    return output
     
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
            if ob2.__class__.__name__ == "EditorState":
                return ob2
        print "_______________________"
    pass


