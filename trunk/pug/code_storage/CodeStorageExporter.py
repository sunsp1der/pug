"Functions for implementing export of python code"

import time
from inspect import isclass, getmro
import os.path
import imp
import sys

from pug.code_storage.constants import _INDENT, _STORE_UNICODE
from pug.component import ComponentObject, Component
from pug.component.ComponentObject import ComponentSet
from pug.gname import GnamedObject
from pug.util import make_name_valid, get_type_name
import all_components

_DEBUG = False

class CodeStorageExporter():
    """Object that manages exporting autocode

The main method for exporting is to create an instance of this object, then
either call exporter.export(filename, object) or add multiple objects by calling
exporter.add_object(object, storageDict) and finally calling 
exporter.export(filename).

The storageDict is a dictionary of info about the object to be stored, and is
used by many methods of CodeStorageExporter. Normally, it is found by checking
the object for an attribute called _codeStorageDict. It can be specified 
explicitly by adding objects with the exporter.add_object method.
Possible entries in storageDict:
    'as_class': autocode creates a python class rather than an object, 
        default is False
    'attributes': list of class attributes to be stored, '*' in list indicates 
        all. Default is all.
    'instance_attributes': When storing an object 'as_class', this list of 
        attributes will be set in the 'init_method' specified below. These 
        attributes will not be stored as class attributes. '*' in list indicates 
        all attributes not listed BY NAME in the 'attributes' list. Default is 
        []. Note that property attributes will always be stored as an 
        instance_attribute. When 'as_class' is false, these attributes are 
        simply added to the attributes list.
    'skip_attributes': list... when using ['*'] above, sometimes it is easier to 
        specify attributes to skip. Default is []. Note that __module__,
        __dict__, and empty __doc__ attributes are always skipped.
    'instance_only_attributes': list... these attributes only appear in 
        instances and are never saved in classes
    'base_class': the class the object is to be saved as. Defaults to the 
        object's class or, if the object is being saved as a class default to
        the object's top parent. TODO: multiple inheritance is not supported
    'init_method': the name of the initialization method of the object. This is 
        used to set instance_attributes when 'as_class' is true. Default is
        '__init__'. If you don't want an init_method automatically created, you
        can set this to ''.
    'init_method_args': arguments to be passed to the init_method. These
        arguments will be passed to the base class' init method as well. If this
        is set to None, there will be no args passed to the init method. This 
        argument should be passed as a list of strings. Default is: 
        ['*args', '**kwargs'] and 'self' is always included.
    'base_init': If this evaluates to True, call the base_class init method. If
        the value is "before", the base_class init will be called before 
        attribute assignments in init_method. Any other value will call the 
        base_class init method after attribute assignments. Default is True
    'base_init_args': The arguments to be passed to the base class init method.
        Default is the value of 'init_method_args' above.
    'force_init_def': always put in the def line for the init method, even if 
        there is no code in the method itself. This is used to facilitate
        custom additions to the method. Default is False
    'name': the name of the object to be stored. If this is not possible or no 
        name is provided, the default is class name for classes or 
        'classname_instance' for objects. Any duplicate names will have a number 
        appended to them. The final name to be used can be found in 
        storageDict['storage_name'] after calling prepare_storageDict. 
    'custom_export_func': this function will be called instead of the usual 
        exporter.create_object_code(). it will be passed the same arguments as
        that function AND also the exporter object itself(obj, storageDict, 
        indentLevel, exporter). The function should return the full code for the
        object. To create the standard export code from within your custom 
        function, remove the 'custom_export_func' entry from storageDict, then 
        call: exporter.create_object_code(obj, storageDict, indentLevel)
    'dummy_creator': CodeStorage uses dummy objects to figure out what attibutes
        need to be stored. Normally dummy creation is done simply by creating an
        object of the stored object's base class. 'dummy_creator' lets you
        specify a function for creating the dummy object. It can be a callable
        object or if you wish to specify a classmethod, use the string name of 
        the method. The function will be called with the exporter object as an 
        argument.        
    'storage_class': always use this class as the base class of classes derived
        from this object
    'storage_name': see 'name' above. DO NOT SET THIS MANUALLY! For reference 
        only!
    'defaults_set': Just a flag indicating that prepare_storageDict has
        been called on the storageDict. DO NOT SET THIS MANUALLY!
"""
    file_changed = False
    code = ''
    filename = ''
    errorfilename = ''
    def __init__(self):
        self.modulesToImport = {} # dict of modules to import
                                  # { 'module':['item1','item2','item3']} etc.
        self.specialImports = {} # { 'module': [[importItem, Name],...]}
                                # from module import importItem as Name
        self.exportDictList = [] # list of objects to be exported when export
                                  # is called. [(obj,storageDict)]
        self.objCode = {} # chunks of object code {'storage_name':code}
        self.storageNames = [] # names of objects in the exported code
        self.deleteCallbacks = [] # fns to be called on delete
        self.dummyDict = {} # dummy objects for attribute comparisons
        
    def register_delete_callback(self, fn):
        """register_delete_callback(self, fn, args, kwargs)
        
fn will be called with exporter as an argument in exporter's __del__ method
"""
        self.deleteCallbacks.append(fn)
        
    def __del__(self):
        for fn in self.deleteCallbacks:
            fn( self)

    def export(self, filename, obj=None, asClass=None, storageDict=None):
        """export(filename, obj=None)
    
Export auto-generated code that will create 'obj'

filename: the file to write to
obj: the object to export. If none provided, export all objects previously
    passed to add_object
storageDict: will be created if necessary (see class definition) 
asClass: If True, force obj to export as a class, if False, force export as 
    an object, if None, use default as set in obj._codeStorageDict or, if not 
    there, default to False.
"""
        self.filename = filename
        # set object
        if obj is not None:
            storageDict = self.add_object (obj, asClass, storageDict)            
        # read old file so we can check for changes
        try:
            oldfile = open(filename, 'r')
        except:
            oldcode = None
            pass
        else:
            oldcode = oldfile.read()
            oldfile.close()
        # create code
        code = ''
        try:
            code = self.create_code()
            exec code           
        except:
            if code:
                self.errorfilename = ''.join([filename,'.err'])
                errorfile = open( self.errorfilename, 'w')
                errorfile.write(code)
                errorfile.close()
                # if there were any problems creating the code, make sure we don't
                # write to the file
                info = ''.join([str(sys.exc_info()[1]), 
                                '\nSaved to: ', self.errorfilename])
                raise sys.exc_info()[0]( info)
            else:
                raise
        # test load
        self.code = code
        if code != oldcode:
            exportfile = open(filename, 'w')
            self.file_changed = True
            exportfile.write(code)
            exportfile.close()
        return self.file_changed
        
    def add_object(self, obj, asClass=None, storageDict=None):
        """add_object(self, obj, storageDict=None)->initialized storageDict
        
Add obj to the list of objects to be exported.
asClass: If True, force obj to export as a class, if False, force export as 
    an object, if None, use default as set in obj._codeStorageDict['as_class']
    or, if not there, default to False.
storageDict: will be created if necessary (see class definition) 
"""
        self.prepare_storageDict(obj, storageDict, asClass)
        self.exportDictList.append( storageDict)
        return storageDict

    def prepare_storageDict(self, obj, storageDict=None, asClass=None):
        """prepare_storageDict(self, obj, storageDict=None):

Set up storageDict.  See CodeStorageExporter documentation for details.
"""
        if storageDict and storageDict.get('defaults_set', False):
            return storageDict
        if storageDict == None:
            storageDict = self.get_custom_storageDict(obj)
        if asClass is not None:
            storageDict['as_class'] = asClass
        storageDict.setdefault('obj', obj)   
        storageDict.setdefault('attributes', ['*'])
        storageDict.setdefault('init_method', '__init__')
        storageDict.setdefault('init_method_args', ['*args','**kwargs'])
        storageDict.setdefault('custom_export_func', None)
        storageDict.setdefault('as_class', False)
        storageDict.setdefault('skip_attributes', [])
        storageDict.setdefault('instance_attributes', [])
        storageDict.setdefault('base_class', None)
        storageDict.setdefault('instance_only_attributes', [])
        storageDict.setdefault('force_init_def', False)
        storageDict.setdefault('base_init', True)
        storageDict.setdefault('base_init_args', 
                               storageDict['init_method_args'])
        # set the default name
        if 'name' in storageDict:
            if not storageDict.get('name'):
                storageDict.pop('name')
        if getattr(obj, 'gname', None) and isinstance(obj, GnamedObject):
            storageDict['gname'] = obj.gname
            if not storageDict.get('name', None):
                storageDict['name'] = obj.gname
        else:
            storageDict['gname'] = None
        if storageDict['as_class']:
            storage_name = storageDict.get('name', get_type_name(obj))
        else:
            if isinstance(obj, Component):
                suffix = '_component'
            else:
                suffix = '_instance'
            storage_name = storageDict.get('name', 
                       ''.join([get_type_name(obj), suffix]).lower())            
        storageDict['storage_name'] = \
                self.create_valid_storage_name(storage_name)
        # base_class and import_module
        if storageDict['base_class']:
            obj_class = storageDict['base_class']
            import_module = obj_class.__module__
        else:
            if isclass(obj):
                #TODO: this won't work for multiple inheritance
                mro = getmro(obj)
                if len(mro) > 1:
                    obj_class = mro[1]
                    import_module = mro[1].__module__
                else:
                    obj_class = None
                    import_module = None
            elif get_type_name(obj) == storageDict['storage_name']:
                if storageDict['as_class']:
                    cls = obj.__class__
                    mro = getmro(cls)
                    obj_class = mro[1]
                    import_module = mro[1].__module__
                else:
                    storageDict['storage_name'] = ''.join(
                                    [storageDict['storage_name'],'_instance'])
                    obj_class = obj.__class__
                    import_module = obj_class.__module__
            else:
                obj_class = obj.__class__
                import_module = obj_class.__module__
            storageDict['base_class'] = obj_class
        storageDict.setdefault('import_module', import_module)              
        storageDict.setdefault('defaults_set', True)
        return storageDict
    
    def create_valid_storage_name(self, name):
        storage_name = make_name_valid(name)
        if storage_name in self.storageNames:
            suffix = 2
            base_name = storage_name
            while storage_name in self.storageNames:
                storage_name = ''.join([base_name, '_', str(suffix)])
                suffix+=1
        self.storageNames.append(storage_name)
        return storage_name
        
    def setup_import(self, module, itemName):   
        """setup_import(module, itemName)->import name
        
module: name of the module to import from
itemName: name of the item to import

Add import info to modulesDict. Returns the import name, which may be different
from itemName due to name conflicts.
"""
        # set up for import statements
        if module is '__builtin__':
            return itemName
        else:
            importName = self.create_valid_storage_name( itemName)
            modulesDict = self.modulesToImport
            specialDict = self.specialImports
            if itemName == importName:
                if modulesDict.has_key(module):
                    modulesDict[module].append(itemName)
                else:
                    modulesDict[module] = [itemName]
            else:
                if modulesDict.has_key(module) and \
                        itemName in modulesDict[module]:
                    return itemName
                if specialDict.has_key(module):
                    self.specialImports[module].append((itemName, importName))
                else:
                    self.specialImports[module] = [(itemName, importName)]
            return importName
        
    def create_code(self):
        """create all the code for exporting"""
        # create code for individual objects
        for storageDict in self.exportDictList:
            obj = storageDict['obj']
            name, objCode = self.create_object_block(obj, storageDict)
            self.objCode.setdefault(name, objCode)
        # create file label
        fname = os.path.basename(self.filename)
        code = [''.join(['"""',fname,'"""\n\n'])]            
        # create code for imports and other initialization
        code += [self.create_import_code()]
        for storageDict in self.exportDictList:
            obj_name = storageDict['storage_name']
            obj_code = self.objCode[obj_name]
            code.append(obj_code)
        allCode = ''.join(code)
        
        return allCode

    def create_object_block(self, obj, storageDict=None):
        """create_object_code(self, obj, storageDict) -> (storage_name, code)

Creates object code including comment blocks before and after.

obj: obj to create block for
storageDict: storageDict to use. If not provided, self.exportDictList will be
    searched for the storageDict that matches obj
"""        
        # create code block
        if storageDict is None:
            for searchStorageDict in self.exportDictList:
                if searchStorageDict['obj'] is obj:
                    storageDict = searchStorageDict
                    break
            # none found, so start from scratch
            storageDict = None
        storageDict = self.prepare_storageDict( obj, storageDict)
        storage_name = storageDict['storage_name']
        label = ''.join(['"', storage_name, '" autocode'])
        startblock = self.create_comment_block(label)
        endblock = self.create_comment_block(''.join(['End ', label]))
        codeblock = self.create_object_code( obj, storageDict)
        code = ''.join([startblock, codeblock, endblock,'\n'])
        return (storage_name, code)

    def get_custom_storageDict(self, obj):
        storageDict = getattr(obj, '_codeStorageDict', {})
        if storageDict:
            storageDict = storageDict.copy()
        return storageDict
        
    def create_object_code(self, obj, storageDict=None, indentLevel=0, 
                           ignoreCustom=False):
        """create_object_code(self, obj, storageDict, indentLevel, ignoreCustom)

obj: the object to make code for. 
storageDict: see class description. Default is None. If None, getStorageInfo 
    will create one
indentLevel: level of indentation before code. Default is 0. An indent level is 
    normally 4 spaces. This can be set be changing the _indent attribute of this
    module.
ignoreCustom: default is False. If True, the storageDict['custom_export_func']
    will be ignored. This is useful when calling this function from within the
    custom export function of an object.
"""
        storageDict = self.prepare_storageDict(obj, storageDict)
        # use custom func if it's provided
        if storageDict.get('custom_export_func') and not ignoreCustom:
            return storageDict['custom_export_func'](obj, storageDict, 
                                                     indentLevel, self)
        else:        
            asClass = storageDict['as_class']
            instantiatorCode = self.create_instantiator_code(obj,
                                                             storageDict,
                                                             indentLevel)
            baseCode = self.create_base_code(obj, storageDict, indentLevel)
            codeList = [instantiatorCode, baseCode]
            if asClass:
                initCode = self.create_init_method(obj, storageDict, indentLevel)
                if not initCode and not baseCode:
                    baseIndent = _INDENT * indentLevel
                    initCode = ''.join([baseIndent, _INDENT, 'pass\n'])
                codeList.append(initCode)
            return ''.join(codeList)
        
    def create_instantiator_code(self, obj, storageDict, indentLevel=0):
        """create_instantiator_code(...) -> code text
        
create_instantiator_code(self, obj, storageDict, indentLevel=0)
        
Create the first line of code (obj instantiation or class decl) and set up 
imports.
"""
        storageDict = self.prepare_storageDict(obj, storageDict)
        import_module = storageDict['import_module']
        base_class = storageDict['base_class']
        name = storageDict['storage_name']
        if import_module and base_class:
            class_name = self.setup_import( import_module, base_class.__name__)
        elif base_class:
            class_name = base_class.__name__

        isClass = storageDict['as_class']
        baseIndent = _INDENT*indentLevel
        if isClass:
            if base_class:
                baseClass = class_name
            else:
                baseClass = ''
            codeList = [baseIndent, 'class ', name, '(', baseClass, '):\n']
        else:
            # put gname in instantiator
            attrList, instanceAttrList = self.create_attribute_lists( obj,
                                                                  storageDict)
            if storageDict.get('gname',False):
                gname_code = ''.join(['gname=',repr(storageDict['gname'])])
            else:
                gname_code = ''            
            codeList = [baseIndent, name, ' = ', class_name, '(',
                        gname_code,')\n']
        return ''.join(codeList)
    
    def create_base_code(self, obj, storageDict, indentLevel=0):
        """create_base_code(...) -> code text
        
create_base_code(self, obj, storageDict, indentLevel=0)
        
Create the code that sets obj's attributes. If storageDict['as_class'] is true, 
then this returns the class attributes only, not the attributes that belong in 
the init method.
"""
        storageDict = self.prepare_storageDict(obj, storageDict)
        isClass = storageDict['as_class']
        baseIndent = _INDENT*indentLevel
        attrList, instanceAttrList = self.create_attribute_lists( obj,
                                                                  storageDict)
        if isClass:
            attributeCode = self.create_attribute_code(obj, storageDict, 
                                                    indentLevel + 1, '',
                                                    attrList)
        else:
            name = storageDict['storage_name']
            attributeCode = self.create_attribute_code(obj, storageDict, 
                                                    indentLevel, 
                                                    ''.join([name,'.']),
                                                    attrList)
        return attributeCode    
    
    def create_init_method(self, obj, storageDict, indentLevel=0, 
                           dodef=True, docode=True):
        """create_init_method(...)
        
args: (self, obj, storageDict, indentLevel=0, dodef=True, docode=True)
dodef: create the def line
docode: create the method code
Create the init_method code. dodef and docode are to facilitate customization.
If storageDict['force_init_def'] is False, dodef is True, docode is True, and
there are no attributes to set, this method returns "". 
"""
        attrList, instanceAttrList = self.create_attribute_lists( obj,
                                                                  storageDict)
        attributeCode = self.create_attribute_code(obj, storageDict, 
                                                   indentLevel + 2, 'self.',
                                                   instanceAttrList)
        if dodef and docode and not attributeCode and \
                                        not storageDict['force_init_def']:
            return '' # no init call necessary
        else:
            codeList = []
            baseIndent = _INDENT*indentLevel
            if dodef:
                initCode = [storageDict['init_method'], '(self']
                if storageDict['init_method_args']:
                    initCode += [', ', 
                                 ', '.join(storageDict['init_method_args'])]
                initCode += [')']                
                codeList += [baseIndent, _INDENT, 'def '] + initCode + [':\n']
            if docode:
                if storageDict['base_init']:
                    # call base class init method
                    initCode = [storageDict['init_method'], '(self']
                    if storageDict['base_init_args']:
                        initCode += [', ',', '.join(storageDict['base_init_args'])]
                    initCode += [')']                
                    baseclass_init=[baseIndent, _INDENT*2, 
                               storageDict['base_class'].__name__,'.'] + \
                               initCode + ['\n']
                    if storageDict['base_init'] == 'before':
                        codeList += baseclass_init
                        codeList.append(attributeCode)
                    else:
                        codeList.append(attributeCode)
                        codeList += baseclass_init
                else:
                    if dodef and docode and not attributeCode:
                        codeList+= [baseIndent, _INDENT * 2, 'pass\n']
                    else:
                        codeList.append(attributeCode)            
            return ''.join(codeList)
    
    def create_attribute_code(self, obj, storageDict, indentLevel=0, prefix='', 
                                attributeList=None):
        if attributeList is None:
            attributeList, instanceAttrList = self.create_attribute_lists( obj,
                                                                  storageDict)        
        storageDict = self.prepare_storageDict(obj, storageDict)
        baseIndent = _INDENT*indentLevel        
        codeList = []
        dummy = self.get_dummy(storageDict['base_class'])
        # create code for requested attributes, if possible
        for attr in attributeList:
            # make sure we can actually get this attribute
            try:
                val = getattr(obj, attr)
            except:
                continue
            # don't bother with callable objects
            if callable(val):
                continue
            if dummy:
                # if we have a dummy, only store object attributes that are 
                # different from the dummy's values
                dummyval = not val
                try:
                    dummyval = getattr(dummy, attr)
                except:
                    pass
                if dummyval == val:
                    continue
                    # For objects that are not builtins, see if they are 
                    # sub-objects. A sub-object is an object that is built into 
                    # an object at creation time.
                        #continue
                        # the code below MIGHT work, but is untested
#                        ######################################################
#                        if getattr(dummyval, '__class__', 0) is \
#                                getattr(val, '__class__', 1):
#                            # it's a sub-object. Try to code_export it
#                            name = storageDict['storage_name']
#                            self.create_subobject_code(val, name, attr, 
#                                                       indentLevel)
#                            
#                            continue
#                        else:
#                            continue                        
#                        continue
#                        #######################################################
            if getattr(val, '__module__', None):
                # this is some kind of non builtin object
                if val.__class__ == ComponentSet:
                    #if it's components store 'em
                    component_code = \
                            self.create_component_code( obj, 
                                                        storageDict, 
                                                        indentLevel)
                    codeList += [component_code]
                    continue
                else:
                    #otherwise only store builtins for now
                    continue
            # random fixes
            if not _STORE_UNICODE and val is unicode(val):
                # we convert unicode values to strings just for pretty's sake
                val = str(val)
            if repr(val) == '-0.0': 
                # I don't totally understand why this is possible
                val = 0.0 
            line = [baseIndent, prefix, attr, ' = ', repr(val), '\n']
            codeList += line
        return ''.join(codeList)

    def set_dummy(self, obj_class, dummy):
        "set_dummy(obj_class, dummy) provide a dummy obj for obj_class"
        self.dummyDict[obj_class] = dummy
        
    def get_dummy(self, obj_class):
        """get_dummy(obj_class) -> a dummy obj of the given class"""
        if not obj_class:
            return None
        dummyDict = self.dummyDict
        if _DEBUG: print "CSE.get_dummy:",obj_class
        if _DEBUG: print "   ",dummyDict
        if obj_class in dummyDict:
            dummy = dummyDict[obj_class]
            if _DEBUG: print "   CSE used cached dummy:", dummy
        else:
            # try for a couple seconds to create a dummy object to compare to
            dummy = None
            try:
                codeStorageDict = getattr(obj_class, '_codeStorageDict', {})
                dummyCreator = codeStorageDict.get('dummy_creator')
                if type(dummyCreator) == str:
                    dummyCreator = getattr(obj_class, dummyCreator)
                if dummyCreator:
                    dummy = dummyCreator( self)
                else:
                    dummy = obj_class()
                starttime = time.time()
                while dummy is None:
                    if time.time() - starttime > 2:
                        break
                    time.sleep(0.01)
            except:
                if _DEBUG:
                    print "   DUMMY OBJECT CREATE FAILED"
                    print sys.exc_info()
                dummy = None
            else:
                if dummy is not None:
                    dummyDict[obj_class] = dummy
                    if _DEBUG: print "   bCSE created dummy" + str(dummy)
                else:
                    # this is a little odd, but necessary due to threading
                    dummy = None
        return dummy

        
    def create_attribute_lists(self, obj, storageDict=None): 
        """create_attributes_lists(obj, storageDict=None)->(attrList, iAttrList)
        
Return the lists of attribute names to attempt to store: attrList, iAttrList
attrList: main attributes to store
iAttrList: When storing 'as_class', these attributes will be set in the init 
    method rather than in the class definition. iAttrList will be empty if 
    'as_class' is False.
"""       
        storageDict = self.prepare_storageDict(obj, storageDict)
        name = storageDict['storage_name']
        attrList = []
        instanceAttrList = []
        # attributes    
        asClass = storageDict['as_class']
        if '*' in storageDict['attributes']:
            if '*' in storageDict['instance_attributes'] and asClass:
                # only use SPECIFIED 'attributes'
                attrList = storageDict['attributes']
                attrList.remove('*')
            else:
                attrList = dir(obj)
            if 'components' in attrList:
                # put components at end
                attrList.remove('components')
                attrList.append('components')
        else:
            attrList = storageDict['attributes']
        if '*' in storageDict['instance_attributes']:
            instanceAttrList = dir(obj)
            if 'components' in instanceAttrList:
                # put components at end
                instanceAttrList.remove('components')
                instanceAttrList.append('components')
        else:
            instanceAttrList = storageDict['instance_attributes']
        if asClass:
            # we're storing as a class, so take care of 'instance_attributes'
            if '*' in storageDict['instance_attributes']:
                for attr in attrList:
                    instanceAttrList.remove(attr)
            # all property attributes should be moved to instanceAttributes
            propList = ['components']
            for attr in attrList:
                if isclass(obj):
                    clsAttr = attr
                else:
                    clsAttr = getattr(obj.__class__, attr, None)
                # properties need to go be instance attributes except gname 
                # which works differently
                if isinstance(clsAttr, property) and attr is not 'gname':
                    propList.append(attr)
            for prop in propList:
                if prop in attrList:
                    attrList.remove( prop)
                    if prop not in instanceAttrList:
                        instanceAttrList.append(prop)
            for attr in storageDict['instance_only_attributes']:
                if attr in attrList:
                    attrList.remove(attr)
                if attr in instanceAttrList:
                    instanceAttrList.remove(attr)
        else:
            for attr in instanceAttrList:
                if attr not in attrList:
                    attrList.append(attr)
            for attr in storageDict['instance_only_attributes']:
                if attr not in attrList:
                    attrList.append(attr)
            instanceAttrList = []
            # we put the gname in instantiator, so don't list it here
            if 'gname' in attrList:
                attrList.remove('gname')
        
        # pull out a few attributes that we never want to save
        skip_attributes = ['__module__', '__dict__']
        skip_attributes += storageDict['skip_attributes']
        # __doc__ is a special case that acts funny...
        if '__doc__' in instanceAttrList:
            skip_attributes.append('__doc__')
        elif '__doc__' in attrList:
            if isclass(obj) and obj.__doc__ == None or \
                    obj.__class__.__doc__ == None:
                skip_attributes.append('__doc__')
        for attr in skip_attributes:
            if attr in attrList:
                attrList.remove( attr)
            if attr in instanceAttrList:
                instanceAttrList.remove(attr)
        return (attrList, instanceAttrList)
       

    def create_subobject_code(self, obj, parentname, attribute, indentLevel=0):
        subStorageDict = getattr(obj, '_codeStorageDict', {})
        subStorageDict['as_class'] = False
        subStorageDict['storage_name'] = ''.join([parentname, '.', attribute])
        sub_code = self.create_base_code(obj, subStorageDict, indentLevel)  
        return sub_code
        

    def create_import_code(self):
        modules = self.modulesToImport.keys()
        modules += self.specialImports.keys()
        if not modules:
            return ''
        importblock = ''
        statement = ''
        startblock = self.create_comment_block('import autocode')
        #import statements
        modules.sort()
        for mod in modules:
            base_statement = ' '.join(['from', mod, 'import'])
            if self.modulesToImport.has_key(mod):
                statement = base_statement
                itemlist = self.modulesToImport[mod]
                count = 0
                for item in itemlist:
                    if count == 0:
                        divider = ' '
                    else:
                        divider = ', '
                    count += 1
                    # create a new line if necessary
                    if len(statement)  + len(divider) + len(item) > 78:
                        divider = ''.join([divider, '\\\n        '])
                    statement = ''.join([statement, divider, item])
                statement = ''.join([statement, '\n'])
                importblock = ''.join([importblock, statement])
            if self.specialImports.has_key(mod):
                infoList = self.specialImports[mod]
                for item in infoList:
                    statement = ' '.join(
                            [base_statement, item[0], 'as', item[1]])
                    importblock = ''.join([importblock, statement,'\n'])
        endblock = self.create_comment_block('End import autocode')
        return ''.join([startblock, importblock, endblock,'\n'])
    
    def create_comment_block(self, comment):
        """comment_block(comment) -> string with comment boxed in #s"""
        l = len(comment)
        startblock = '#' * (l + 4)
        comment = ''.join(['# ', comment, ' #'])
        return '\n'.join([startblock, comment, startblock, '']) 
    
    def create_component_code(self, obj, storageDict, indentLevel=0):
        storageDict = self.prepare_storageDict(obj, storageDict)
        dummy = self.get_dummy(storageDict['base_class'])
        componentCode = []
        if storageDict['as_class']:
            parentName = 'self'
        else:
            parentName = storageDict['storage_name']
        componentList = obj.components.get()
        try:
            dummyList = dummy.components.get()
        except:
            dummyList = []
        # component adding code
        for comp in componentList:
            duplicate = False
            for dummyComp in dummyList:
                if dummyComp.is_duplicate_of(comp):
                    dummyList.remove(dummyComp)
                    duplicate = True
                    break      
            if duplicate:
                continue      
            compStorageDict = self.get_custom_storageDict(comp)
            compStorageDict['as_class'] = False
            compStorageDict = self.prepare_storageDict(comp, compStorageDict)
            compObjClass = compStorageDict['base_class']
            compImportModule = compStorageDict['import_module']
            # just drop in the all_components magic
            if all_components and compObjClass.__name__ in dir(all_components):
                import_name = self.setup_import('all_components', 
                                                compObjClass.__name__)     
            else:                               
                import_name = self.setup_import(compImportModule, 
                                                compObjClass.__name__)
            
            comp_code = [indentLevel * _INDENT, parentName, '.components.add( ',
                            import_name,'(']
            comp_code += [comp._create_argument_code(indentLevel)]
            componentCode += comp_code
            componentCode += [') )\n']
        # component removal code
        for comp in dummyList:
            compStorageDict = self.get_custom_storageDict(comp)
            compStorageDict['as_class'] = False
            compStorageDict = self.prepare_storageDict(comp, compStorageDict)
            compObjClass = compStorageDict['base_class']
            compImportModule = compStorageDict['import_module']
            if all_components and compObjClass.__name__ in dir(all_components):
                import_name = self.setup_import('all_components', 
                                                compObjClass.__name__)     
            else:                               
                import_name = self.setup_import(compImportModule, 
                                                compObjClass.__name__)
            comp_code = [indentLevel * _INDENT, parentName, 
                         '.components.remove_duplicate_of( ', import_name,'(']
            comp_code += [comp._create_argument_code(indentLevel)]
            componentCode += comp_code
            componentCode += [') )\n']            
        return ''.join(componentCode)