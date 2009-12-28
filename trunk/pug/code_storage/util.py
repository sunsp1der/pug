from pug.code_storage import CodeStorageExporter

def code_export( obj, filename, asClass=False, storageDictUpdate = {}):
    """code_export(obj, filename, asClass, storageDict)->exporter

Simple export of object obj to filename  
asClass: If True, force export as a class, if False, force export as an object,
    if None, use default as set in obj._codeStorageDict or, if not there, 
    default to export as object (False).
storageDictUpdate: This dict will be used to update obj's storageDict for this
    export (useful for names)
The exporter is returned, which has some useful attributes including 'code' with
the exported code and 'file_changed' which tells if the resulting file was
actually different from the original, 'filename', 'errfilename' etc.
"""    
    exporter = CodeStorageExporter()
    dict = getattr(obj, '_codeStorageDict', {}).copy()
    dict.update(storageDictUpdate)
    exporter.export(filename, obj, asClass, dict)
    return exporter

def add_subclass_attributes( storageDict, subclass):
    """add_subclass_attributes( storageDict, subclass)->list of adds
    
Add subclass's codeStorageDict's attributes to storageDict. This will take care
of name mangling as well
"""
    subDict = getattr(subclass,'_codeStorageDict',{})
    subAttributes = subDict.get('attributes',[])
    if subAttributes and not(storageDict.get('attributes')):
        storageDict['attributes'] = []
    list = storageDict['attributes']
    addList = []
    for attribute in subAttributes:
        if attribute.startswith('__'):
            attribute = ''.join(['_',subclass.__name__,attribute])
        if attribute in list:
            continue
        addList.append(attribute)
    list+=addList
    return addList
    
def add_subclass_skip_attributes( storageDict, subclass):
    """add_subclass_skip_attributes( storageDict, subclass)->list of adds
    
Add subclass's codeStorageDict's skip_attributes to storageDict. This will take 
care of name mangling as well
"""
    subDict = getattr(subclass,'_codeStorageDict',{})
    subAttributes = subDict.get('skip_attributes',[])
    if subAttributes and not(storageDict.get('skip_attributes')):
        storageDict['skip_attributes'] = []
    list = storageDict['skip_attributes']
    addList = []
    for attribute in subAttributes:
        if attribute.startswith('__'):
            attribute = ''.join(['_',subclass.__name__,attribute])
        if attribute in list:
            continue
        addList.append(attribute)
    list+=addList
    return addList 
