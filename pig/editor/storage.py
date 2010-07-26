"""storage.py

loading and saving utility code"""

def save_object(obj, name=None, parentWindow=None):
    """save_object(obj): Export obj as a class to objects folder

name: the name to save the object as. If not provided, a dialog will be opened
parentWindow: the parent window of name dialog. If not provided, the 
    wx.ActiveWindow will be used
"""
    if not isinstance(obj, Node):
        raise TypeError('save_object() arg 1 must be a Node')
    if not name:
        if obj.archetype:
            name = obj.gname
        else:
            if obj.gname:
                name = obj.gname+"Class"
            else:
                name = "MyClass"
        if not name:
            name = obj.__class__.__name__
        if parentWindow == None:
            parentWindow = wx.GetActiveWindow()
        objName = ''
        # we generally don't want to save with the same name as 
        # a base class of the same object
        superclasses = getmro(obj.__class__)[1:]
        for cls in superclasses:
            if name == cls.__name__ or name=='Sprite' or name=='PigSprite':
                name = ''.join(['My',name])
                break
        default = make_valid_attr_name(name)
        dlg = wx.TextEntryDialog( parentWindow, 
                                  "Enter the object's class/file name", 
                                  "Save Object", default)
        while not objName:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                errorDlg = None
                if name == 'PigSprite' or name == 'Sprite':
                    errorDlg = wx.MessageDialog( dlg, 
                           "You can't use the names 'PigSprite' or 'Sprite'",
                           "Reserved Name",
                           wx.OK)
                elif name != make_valid_attr_name(name):
                    errorDlg = wx.MessageDialog( dlg, 
                           "Name cannot contain spaces or special characters"+\
                           "\nand cannot start with a number",
                           "Invalid Name",
                           wx.OK)
                if errorDlg:   
                    errorDlg.ShowModal()
                    errorDlg.Destroy() 
                    dlg.SetValue(default)
                    dlg.SetFocus()      
                    continue                
                path = os.path.join('objects',''.join([name,'.py']))
                if name != default:
                    # verify overwrite
                    try:
                        test = file(path)
                    except:
                        objName = name
                    else:
                        test.close()
                        confirmDlg = wx.MessageDialog( dlg, 
                                "\n".join([path,
                               "File already exists. Overwrite?"]),
                               "Confirm Replace",
                               wx.YES_NO | wx.NO_DEFAULT)
                        if confirmDlg.ShowModal() == wx.ID_YES:
                            objName = name
                        confirmDlg.Destroy()
                else:
                    objName = name
            else:
                dlg.Destroy()
                return
        dlg.Destroy()
    else:
        objName = name
        path = os.path.join('objects',''.join([name,'.py']))
    try:
        if getattr(obj, 'archetype', False):
            # we don't want every instance to be an archetype
            obj.archetype = False
            archetype = True
        else:
            archetype = False    
        try: 
            pigsprite = PigSprite
        except:
            from pig.PigSprite import PigSprite
        exporter = code_export( obj, path, True, {'name':objName,
                                                  'base_class':PigSprite})
        objDict = get_available_objects( True)
        oldclass = obj.__class__
        if oldclass != objDict[objName]:
            obj.__class__ = objDict[objName]            
        if archetype:
            # return archetype status after saving
            obj.archetype = True
            if exporter.file_changed:
                archetype_changed( obj, oldclass, exporter)
        return exporter
    except:
        show_exception_dialog()
    
_changedArchetypeList = []    
def archetype_changed( archetype, oldclass, archetype_exporter=None):
    if archetype_exporter is None:
        archetype_exporter = CodeStorageExporter()
    newclass = archetype.__class__
    # convert all nodes referencing this archetype
    new_dummy = archetype_exporter.get_dummy(newclass)
    old_dummy = archetype_exporter.get_dummy(oldclass)
    nodes = PigDirector.scene.nodes
    storageDict = archetype_exporter.get_custom_storageDict(new_dummy)
    storageDict['as_class'] = False 
    attributeList = archetype_exporter.create_attribute_lists(
                                            new_dummy, storageDict)[0]                                                        
    for changer in nodes:
        if changer == old_dummy or changer == new_dummy or changer == archetype:
            # just a temporary object used by this process
            continue
        if not (changer.__class__.__name__ == newclass.__name__ and \
                    changer.__class__.__module__ == newclass.__module__):
            # not of the archetype's class
            continue
        if _DEBUG: print "archetype_changed changer:", changer
        old_dummy = archetype_exporter.get_dummy(changer.__class__)
        changer.__class__ = newclass
        # convert the object to new archetype form
        # set attributes
        for attr in attributeList:
            try:
                oldval = getattr(old_dummy, attr)
                newval = getattr(new_dummy, attr)
            except:
                continue
            if oldval == newval:
                continue
            setVal = False
            try:
                val = getattr(changer, attr)
            except:
                setVal = True
            if getattr(newval, '__module__', False):
                valtype = type(newval)
                if valtype == VectorReference:
                    setVal = val.x == oldval.x and val.y == oldval.y
                elif valtype == ImageInstance:
                    setVal = True
                else:
                    continue
            if setVal or val == oldval:
                try:
                    setattr(changer, attr, newval)
                except:
                    continue
        # set components
        oldComponents = old_dummy.components.get()
        if _DEBUG: print "archetype_changed oldComponents:", oldComponents
        newComponents = new_dummy.components.get()
        if _DEBUG: print "archetype_changed newComponents:", newComponents
        if _DEBUG: print "archetype_changed changer components:",\
                                                    changer.components.get()
        for comp in oldComponents:
            removed = changer.components.remove_duplicate_of(comp)
            if not removed:
                # if component is in new and old but not changer, don't add it!
                dupecomp = new_dummy.components.get_duplicate_of(comp)
                if dupecomp:
                    if _DEBUG: print "archetype_changed: don't add", dupecomp
                    newComponents.remove(dupecomp)
            else:
                if _DEBUG: print "archetype_changed: removed", comp

        for comp in newComponents:
            # add duplicate components
            if not changer.components.get_duplicate_of(comp):
                if _DEBUG: print "archetype_changed: add", comp
                changer.components.add(copy(comp))
    
def save_scene():
    """Save scene to disk"""
    name = PigDirector.scene.__class__.__name__
    return save_scene_as(name)
        
def save_scene_as( sceneName=None, fileName=None):#, parentWindow=None):
    """save_scene_as( sceneName=None, fileName=None)->Filename or False if fail 
    Save the current scene as a class in the scenes folder
        
sceneName: string with name to save as. If None, a dialog will be opened.
parentWindow: the parent window of name dialog. If not provided, the 
    wx.ActiveWindow will be used
"""
    wx.GetApp().apply()
    if get_scene_errors():
        return False
    if _DEBUG: print "util: save_scene_as"
    scene = PigDirector.scene
    if not sceneName:
        name = scene.__class__.__name__
        if name == 'PigScene' or name == 'Scene':
            name = 'MyScene'
        name = make_valid_attr_name(name)
        name.capitalize()
        if _DEBUG: print "util: save_scene_as 1"
        parentWindow=None
        if parentWindow == None:
            parentWindow = wx.GetActiveWindow()
        default = make_valid_attr_name(name)
        dlg = wx.TextEntryDialog( parentWindow, 
                                  "Enter the scene's class/file name", 
                                  "Save Scene", default)
        if _DEBUG: print "util: save_scene_as 2"
        while not sceneName:
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                errorDlg = None
                if name == 'PigScene' or name == 'Scene':
                    errorDlg = wx.MessageDialog( dlg, 
                           "You can't use the names 'PigScene' or 'Scene'",
                           "Reserved Name",
                           wx.OK)
                elif name != make_valid_attr_name(name):
                    errorDlg = wx.MessageDialog( dlg, 
                           "Name cannot contain spaces or special characters"+\
                           "\nand cannot start with a number",
                           "Invalid Name",
                           wx.OK)
                if errorDlg:    
                    errorDlg.ShowModal()
                    errorDlg.Destroy() 
                    dlg.SetValue(default)
                    dlg.SetFocus()      
                    continue
                path = os.path.join('scenes',''.join([name,'.py']))
                if name != default:
                    try:
                        test = file(path)
                    except:
                        sceneName = name
                    else:
                        test.close()
                        confirmDlg = wx.MessageDialog( dlg, 
                               "Scene file already exists. Overwrite?",
                               "Confirm Replace",
                               wx.YES_NO | wx.NO_DEFAULT)
                        if confirmDlg.ShowModal() == wx.ID_YES:
                            sceneName = name
                        confirmDlg.Destroy()   
                else:    
                    sceneName = name             
            else:
                dlg.Destroy()
                return False
        dlg.Destroy()
    else:
        if sceneName == 'PigScene' or sceneName == 'Scene':
            raise ValueError("Can't save over 'PigScene' or 'Scene'")
#            save_scene_as( sceneName, fileName)
    if not fileName:
        fileName = ''.join([sceneName, '.py'])
    path = os.path.join('scenes',fileName)
    app = wx.GetApp()
    if _DEBUG: print "util: save_scene_as 4"
    selection = app.selectedObjectDict.keys()
    oldscene = PigDirector.scene
    wait_for_state( None)
    if _DEBUG: print "util: save_scene_as 5"
    wx.BeginBusyCursor()
    saved = False
    try:
        if _DEBUG: print "util: save_scene_as enter code_export"
        code_export( scene, path, True, {'name':sceneName})
        if _DEBUG: print "util: save_scene_as exit code_export"
    except:
        if _DEBUG: print "util: save_scene_as 6"        
        show_exception_dialog()
    else:
        if _DEBUG: print "util: save_scene_as 7"        
        sceneDict = get_available_scenes(True)
        PigDirector.scene.__class__ = sceneDict[sceneName]
        saved = True
    finally:
        wx.EndBusyCursor()        
        if PigDirector.scene != oldscene:
            wx.GetApp().set_selection([])
            if _DEBUG: print "util: save_scene_as reset select:", selection        
        wait_for_state(EditorState)

        wx.GetApp().refresh()
    if saved:
        return fileName
    else:
        return False
          

