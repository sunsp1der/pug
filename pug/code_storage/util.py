from pug.code_storage import CodeStorageExporter

def code_exporter( obj, filename=None, asClass=False, storageDictUpdate = {}, 
                 test=None):
    """code_exporter(obj, filename, asClass, storageDict, test)->exporter

Simple export of object obj to filename or simply return exporter with code to
be exported in 'code' attribute
filename: name of file. None means don't automatically save.
asClass: If True, force export as a class, if False, force export as an object,
    if None, use default as set in obj._codeStorageDict or, if not there, 
    default to export as object (False).
storageDictUpdate: This dict will be used to update obj's storageDict for this
    export (useful for names)
test: if True, test the code for exceptions. WARNING: Testing actually executes
    code, so objects may be instantiated... Defaults to same value as asClass
The exporter is returned, which has some useful attributes including 'code' with
the exported code and 'file_changed' which tells if the resulting file was
actually different from the original, 'filename', 'errfilename' etc.
"""    
    exporter = CodeStorageExporter()
    dict = getattr(obj, '_codeStorageDict', {}).copy()
    dict.update(storageDictUpdate)
    if test is None:
        test = asClass
    exporter.export(filename, obj, asClass, dict, test)
    return exporter

def add_subclass_storageDict_key( storageDict, subclass,key='skip_attributes'):
    """add_subclass_storageDict_info( storageDict, subclass, key)->list of adds
    
Add subclass's codeStorageDict's info from 'key' to storageDict. This will take 
care of name mangling as well. Generally used for keys: attributes, and
skip_attributes.
"""
    subDict = getattr(subclass,'_codeStorageDict',{})
    subAttributes = subDict.get(key,[])
    if subAttributes and not(storageDict.get(key)):
        storageDict[key] = []
    list = storageDict[key]
    addList = []
    for attribute in subAttributes:
        if attribute.startswith('__'):
            attribute = ''.join(['_',subclass.__name__,attribute])
        if attribute in list:
            continue
        addList.append(attribute)
    list+=addList
    return addList     