"Functions for implementing export of python code"

import time
from inspect import isclass, getmro
import os.path
import compiler

from pug.code_storage.constants import _INDENT, _STORE_UNICODE
from pug.component import ComponentObject, Component
from pug.component.ComponentObject import ComponentSet
from pug.gname import GnamedObject
from pug.util import make_name_valid, get_type_name
import all_components

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
    'init_method': the name of the initialization method of the object. This is 
        used to set instance_attributes when 'as_class' is true. Default is
        '__init__'. If you don't want an init_method automatically created, you
        can set this to ''.
    'init_method_args': arguments to be passed to the init_method. These
        arguments will be passed to the base class' init method as well. If this
        is set to None, there will be no args passed to the init method AND the
        base class' init method will not be called. This argument should be
        passed as a list of strings. Default is: ['*args', '**kwargs']
    'name': the name of the object to be stored. If this is not possible or no 
        name is provided, the default is class name for templates or 
        'classname_instance' for objects. Any duplicate names will have a number 
        appended to them. The final name to be used can be found in 
        storageDict['storage_name'] after calling set_storageDict_defaults. 
        TODO: The value will be converted to a valid variable name. 
    'custom_export_func': this function will be called instead of the usual 
        exporter.create_object_code(). it will be passed the same arguments as
        that function AND also the exporter object itself(obj, storageDict, 
        indentLevel, exporter). The function should return the full code for the
        object. To create the standard export code from within your custom 
        function, remove the 'custom_export_func' entry from storageDict, then 
        call: exporter.create_object_code(obj, storageDict, indentLevel)
    'storage_class': always use this class as the base class of classes derived
        from this object
    'storage_name': see 'name' above. DO NOT SET THIS MANUALLY! For reference 
        only!
    'defaults_set': Just a flag indicating that set_storageDict_defaults has
        been called on the storageDict. DO NOT SET THIS MANUALLY!
    'dummy_list': any dummy objects created will be placed here in case special
        measures need to be taken to delete them. If necessary, these measures 
        must be in the custom_export_func. Default is []. DO NOT SET MANUALLY
"""
    def __init__(self):
        self.modulesToImport = {} # dict of modules to import
                                  # { 'module':['item1','item2','item3']} etc.
        self.objectsToExport = [] # list of objects to be exported when export
                                  # is called. [(obj,storageDict)]
        self.objCode = {} # chunks of object code {'storage_name':code}
        self.storage_names = []

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
        if obj is not None:
            storageDict = self.add_object (obj, asClass, storageDict)
        try:
            fname = os.path.basename(filename)
            label = ''.join(['"""',fname,'"""\n\n'])
            code = ''.join([label, self.create_code()])
            exportfile = open(filename, 'w')
        except:
            # if there were any problems creating the code, make sure we don't
            # write to the file
            raise
            return
        compiler.parse(code)            
        exportfile.write(code)
        exportfile.close()
        
    def add_object(self, obj, asClass=None, storageDict=None):
        """add_object(self, obj, storageDict=None)->initialized storageDict
        
Add obj to the list of objects to be exported.
asClass: If True, force obj to export as a class, if False, force export as 
    an object, if None, use default as set in obj._codeStorageDict['as_class']
    or, if not there, default to False.
storageDict: will be created if necessary (see class definition) 
"""
        if storageDict is None:
            storageDict = getattr(obj, '_codeStorageDict', {}).copy()
        if asClass is not None:
            storageDict['as_class']=asClass
        if not storageDict.get('defaults_set'):
            self.set_storageDict_defaults(obj, storageDict)
        self.objectsToExport.append((obj, storageDict))
        return storageDict

    def set_storageDict_defaults(self, obj, storageDict):
        """set_storageDict_defaults(self, obj, storageDict):

Set up default values for storageDict.  See CodeStorageExporter documentation 
for details.
"""
        if storageDict.get('defaults_set'):
            return
            
        storageDict.setdefault('attributes', ['*'])
        storageDict.setdefault('init_method', '__init__')
        storageDict.setdefault('init_method_args', ['*args','**kwargs'])
        storageDict.setdefault('custom_export_func', None)
        storageDict.setdefault('as_class', False)
        storageDict.setdefault('skip_attributes', [])
        storageDict.setdefault('instance_attributes', [])
        storageDict.setdefault('dummy_list', [])
        # set the default name
        # TODO: convert name to valid variable name
        if 'name' in storageDict:
            if not storageDict.get('name'):
                storageDict.pop('name')
        else:
            if getattr(obj, 'gname', None) and isinstance(obj, GnamedObject):
                storageDict['name'] = obj.gname
                storageDict['gname'] = obj.gname
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
        if storage_name in self.storage_names:
            suffix = 2
            base_name = storage_name
            while storage_name in self.storage_names:
                storage_name = ''.join([base_name, '_', str(suffix)])
                suffix+=1
        self.storage_names.append(storage_name)
        storageDict['storage_name'] = make_name_valid(storage_name)
              
        storageDict.setdefault('defaults_set', True)
    
    def add_import(self, module, item):   
        """add_import(module, import): add import info to modulesDict 
    
module: the module to import from
item: the item to import
"""
        # set up for import statements
        if module is not '__builtin__':
            modulesDict = self.modulesToImport
            if modulesDict.has_key(module):
                imports = modulesDict[module]
                if item in imports:
                    return
                imports.append(item)
            else:
                modulesDict[module] = [item]
        
    def create_code(self):
        """create all the code for exporting"""
        # create code for individual objects
        for obj, storageDict in self.objectsToExport:
            name, code = self.create_object_block(obj, storageDict)
            self.objCode.setdefault(name, code)
        
        # create code for imports and other initialization
        code = [self.create_import_code()]
        for obj, storageDict in self.objectsToExport:
            obj_name = storageDict['storage_name']
            obj_code = self.objCode[obj_name]
            code.append(obj_code)
        allCode = ''.join(code)
        
        return allCode

    def create_object_block(self, obj, storageDict=None):
        """create_object_code(self, obj, storageDict) -> (storage_name, code)

Creates object code including comment blocks before and after.

obj: obj to create block for
storageDict: storageDict to use. If not provided, self.objectsToExport will be
    searched for the storageDict that matches obj
"""        
        # create code block
        if storageDict is None:
            for searchObj, searchStorageDict in self.objectsToExport:
                if searchObj is obj:
                    storageDict = searchStorageDict
                    break
            # none found, so start from scratch
            storageDict = {}
        storageDict = self.get_storage_info(obj, storageDict)[0]
        storage_name = storageDict['storage_name']
        label = ''.join(['"', storage_name, '" autocode'])
        startblock = self.create_comment_block(label)
        endblock = self.create_comment_block(''.join(['End ', label]))
        codeblock = self.create_object_code(obj, storageDict)
        code = ''.join([startblock, codeblock, endblock,'\n'])
        return (storage_name, code)
    
    def get_storage_info(self, obj, storageDict=None):
        """get_storage_info(self, obj, storageDict=None) 
        
return (storage name, object class, module). set_storageDict_defaults will be
called on storageDict if necessary.

obj: obj to get info for
storageDict: the storageDict to use. If not provided, a copy of the object's 
    _codeStorageDict attribute will be used. If that doesn't exist, defaults
    will be used.
"""
        if storageDict is None:
            storageDict = self.get_custom_storageDict(obj)
        if not storageDict.get('defaults_set'):
            self.set_storageDict_defaults(obj, storageDict)
        obj_class = storageDict.get('base_class', None)
        if obj_class:
            import_module = obj_class.__module__
        else:
            if isclass(obj):
                #TODO: this won't work for multiple inheritance
                mro = getmro(obj)
                if len(mro) > 1:
                    obj_class = mro[1]
                    import_module = mro[1].__module__
                else:
                    obj_class = ""
                    import_module = None
            elif get_type_name(obj) == storageDict['storage_name']:
                cls = obj.__class__
                mro = getmro(cls)
                obj_class = mro[1]
                import_module = mro[1].__module__
            else:
                obj_class = obj.__class__
                import_module = obj_class.__module__
            storageDict['base_class']=obj_class
        return (storageDict, obj_class, import_module)

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
        storageDict, obj_class, import_module = \
                                        self.get_storage_info(obj, storageDict)
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
                initCode = self.create_init_code(obj, storageDict, indentLevel)
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
        storageDict, obj_class, import_module = \
                                        self.get_storage_info(obj, storageDict)
        name = storageDict['storage_name']
        if import_module and obj_class:
            self.add_import(import_module, obj_class.__name__)

        isClass = storageDict['as_class']
        baseIndent = _INDENT*indentLevel
        if isClass:
            if obj_class:
                baseClass = obj_class.__name__
            else:
                baseClass = ''
            codeList = [baseIndent, 'class ', name, '(', 
                        baseClass, '):\n']
        else:
            # put gname in instantiator
            attrList, instanceAttrList = self.create_attribute_lists( obj,
                                                                  storageDict)
            if storageDict.get('gname',False):
                gname_code = ''.join(['gname=',repr(storageDict['gname'])])
            else:
                gname_code = ''            
            codeList = [baseIndent, name, ' = ', obj_class.__name__, '(',
                        gname_code,')\n']
        return ''.join(codeList)
    
    def create_base_code(self, obj, storageDict, indentLevel=0):
        """create_base_code(...) -> code text
        
create_base_code(self, obj, storageDict, indentLevel=0)
        
Create the code that sets obj's attributes. If storageDict['as_class'] is true, 
then this returns the class attributes only, not the attributes that belong in 
the init method.
"""
        storageDict, obj_class, import_module = \
                                        self.get_storage_info(obj, storageDict)
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
    
    def create_init_code(self, obj, storageDict, indentLevel=0):
        """create_init_code(self, obj, storageDict, indentLevel=0)
        
Create the init_method code.
"""
        attrList, instanceAttrList = self.create_attribute_lists( obj,
                                                                  storageDict)
        attributeCode = self.create_attribute_code(obj, storageDict, 
                                                   indentLevel + 2, 'self.',
                                                   instanceAttrList)
        if not attributeCode:
            return ''
        else:
            baseIndent = _INDENT*indentLevel
            initCode = [storageDict['init_method'], '(self']
            argList = storageDict['init_method_args']
            if argList:
                for arg in argList:
                    initCode+=[',',arg]
            initCode += [')']                
            codeList = [baseIndent, _INDENT, 'def '] + initCode + [':\n']
            codeList.append(attributeCode)            
            if storageDict['init_method_args'] != None:
                # call base class init method
                codeList+=[baseIndent, _INDENT*2, 
                           storageDict['base_class'].__name__,'.'] + \
                           initCode + ['\n']
            return ''.join(codeList)
    
    def create_attribute_code(self, obj, storageDict, indentLevel, prefix, 
                                attributeList):
        storageDict, obj_class, import_module = \
                                        self.get_storage_info(obj, storageDict)
        baseIndent = _INDENT*indentLevel        
        codeList = []
        dummyList = storageDict['dummy_list']
        if dummyList:
            dummy = dummyList[0]
        else:
            # try for a couple seconds to create a dummy object to compare to
            dummy = None
            if not isclass(obj):
                try:
                    dummy = obj_class()
                    starttime = time.time()
                    while dummy is None:
                        if time.time() - starttime > 2:
                            break
                        time.sleep(0.01)
                except:
                    dummy = None
                else:
                    if dummy is not None:
                        dummyList.append(dummy)
                    else:
                        # this is a little odd, but necessary due to threading
                        dummy = None
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
        
    def create_attribute_lists(self, obj, storageDict=None): 
        """create_attributes_lists(obj, storageDict=None)->(attrList, iAttrList)
        
Return the lists of attribute names to attempt to store: attrList, iAttrList
attrList: main attributes to store
iAttrList: When storing 'as_class', these attributes will be set in the init 
    method rather than in the class definition. iAttrList will be empty if 
    'as_class' is False.
"""       
        storageDict, obj_class, import_module = \
                                        self.get_storage_info(obj, storageDict)
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
                attrList.remove('components')
                attrList.append('components')
        else:
            attrList = storageDict['attributes']
        if '*' in storageDict['instance_attributes']:
            instanceAttrList = dir(obj)
            if 'components' in instanceAttrList:
                instanceAttrList.remove('components')
                instanceAttrList.append('components')
        else:
            instanceAttrList = storageDict['instance_attributes']
        if asClass:
            # we're storing as a class, so take care of 'instance_attributes'
            if '*' in storageDict['instance_attributes']:
                for attr in attrList:
                    instanceAttrList.remove(attr)
            # all property attributes should be moved to InitAttributes
            propList = ['components']
            for attr in attrList:
                if isclass(obj):
                    clsAttr = attr
                else:
                    clsAttr = getattr(obj.__class__, attr, None)
                # properties need to go be instance attributes except gname 
                # which works nice and fancy-like
                if isinstance(clsAttr, property) and attr is not 'gname':
                    propList.append(attr)
            for prop in propList:
                if prop in attrList:
                    attrList.remove( prop)
                    if prop not in instanceAttrList:
                        instanceAttrList.append(prop)
        else:
            for attr in instanceAttrList:
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
        if '__doc__' in attrList:
            if isclass(obj) and obj.__doc__ == None or \
                    obj.__class__.__doc__ == None:
                skip_attributes.append('__doc__')
        for attr in skip_attributes:
            if attr in attrList:
                attrList.remove( attr)
            if attr in instanceAttrList:
                instanceAttrList.remove(attr)
        return (attrList, instanceAttrList)
       

    def create_subobject_code(self, obj, parentname, attribute, indentLevel):
        subStorageDict = getattr(obj, '_codeStorageDict', {})
        subStorageDict['as_class'] = False
        subStorageDict['storage_name'] = ''.join([parentname, '.', attribute])
        sub_code = self.create_base_code(obj, subStorageDict, 
                                           indentLevel )  
        return sub_code
        

    def create_import_code(self):
        modules = self.modulesToImport.keys()
        if not modules:
            return ''
        importblock = ''
        statement = ''
        startblock = self.create_comment_block('import autocode')
        #import statements
        modules.sort()
        for mod in modules:
            itemlist = self.modulesToImport[mod]
            statement = ''.join(['from ', mod, ' import'])
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
        endblock = self.create_comment_block('End import autocode')
        return ''.join([startblock, importblock, endblock,'\n'])
    
    def create_comment_block(self, comment):
        """comment_block(comment) -> string with comment boxed in #s"""
        l = len(comment)
        startblock = '#' * (l + 4)
        comment = ''.join(['# ', comment, ' #'])
        return '\n'.join([startblock, comment, startblock, '']) 
    
    def create_component_code(self, obj, storageDict, indentLevel):
        storageDict, obj_class, import_module = \
                self.get_storage_info(obj, storageDict)
        componentCode = []
        if storageDict['as_class']:
            parentName = 'self'
        else:
            parentName = storageDict['storage_name']
        componentList = obj.components.get()
        for comp in componentList:
            compStorageDict = self.get_custom_storageDict(comp)
            compStorageDict['as_class'] = False
            compStorageDict, compObjClass, compImportModule = \
                                    self.get_storage_info(comp, compStorageDict)
            # just drop in the all_components magic
            if compObjClass.__name__ in dir(all_components):
                self.add_import('all_components', compObjClass.__name__)     
            else:                               
                self.add_import(compImportModule, compObjClass.__name__)
            
            comp_code = [indentLevel * _INDENT, parentName, '.components.add( ',
                            comp.__class__.__name__,'(']
            comp_code += [comp._create_argument_code(indentLevel)]
            componentCode += comp_code
            componentCode += [') )\n']
        return ''.join(componentCode)