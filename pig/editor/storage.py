"""storage.py

loading and saving utility code"""

import os
import os.path
from inspect import getmro
from copy import copy
import sys

import wx
wx=wx

from Opioid2D.public.Node import Node
from Opioid2D.public.Vector import VectorReference
from Opioid2D.public.Image import ImageInstance

from pug import code_exporter, CodeStorageExporter
from pug.util import make_valid_attr_name
from pug.syswx.util import show_exception_dialog

from pig.util import get_available_scenes, get_available_objects
from pig.PigDirector import PigDirector

_DEBUG = False #

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
                name = obj.gname
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
            if name == cls.__name__ or name=='Sprite':
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
                if name == 'Sprite':
                    errorDlg = wx.MessageDialog( dlg, 
                           "You can't use the names 'Sprite'",
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
                old_module = obj.__class__.__module__.split('.')
                if old_module[-2:-1][0] == 'objects' and \
                        old_module[-1:][0] != name:
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
                            if sys.platform == "win32":
                                files = os.listdir('objects')
                                testname = name + '.py'
                                for f in files:
                                    if f.lower() == testname.lower():
                                        sceneName = os.path.splitext(f)[0]
                                        break
                            else:
                                objName = name
                        confirmDlg.Destroy()
                else:
                    objName = name
            else:
                dlg.Destroy()
                return
        dlg.Destroy()
    else:
        name = make_valid_attr_name(name)
        objName = name
        path = os.path.join('objects',''.join([name,'.py']))
    try:
        if getattr(obj, 'archetype', False):
            # we don't want every instance to be an archetype
            obj.archetype = False
            archetype = True
        else:
            archetype = False    
        from pig.Sprite import Sprite
        exporter = code_exporter( obj, path, True, {'name':objName,
                                                  'base_class':Sprite})
        objDict = get_available_objects( True)
        oldclass = obj.__class__
        if oldclass != objDict[objName]:
            obj.__class__ = objDict[objName]            
        if archetype:
            # return archetype status after saving
            obj.archetype = True
            obj.gname = objName
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
    name = PigDirector.scene.__class__.__name__ #@UndefinedVariable
    if name == "Scene":
        name = None
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
        if name == 'Scene':
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
                if name == 'Scene':
                    errorDlg = wx.MessageDialog( dlg, 
                           "You can't use the name 'Scene'",
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
                path = os.path.join('scenes', name + '.py')
                if name != scene.__class__.__name__:
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
                            if sys.platform == "win32":
                                files = os.listdir('scenes')
                                testname = name + '.py'
                                for f in files:
                                    if f.lower() == testname.lower():
                                        sceneName = os.path.splitext(f)[0]
                                        break
                            else:
                                sceneName = name
                        confirmDlg.Destroy()   
                else:    
                    sceneName = name             
            else:
                dlg.Destroy()
                return False
        dlg.Destroy()
    else:
        if sceneName == 'Scene':
            raise ValueError("Can't save over baseclass 'Scene'")
#            save_scene_as( sceneName, fileName)
    if not fileName:
        fileName = ''.join([sceneName, '.py'])
    path = os.path.join('scenes',fileName)
    app = wx.GetApp()
    if _DEBUG: print "util: save_scene_as 4"
    selection = app.selectedObjectDict.keys()
    oldscene = PigDirector.scene
    from pig.editor.util import wait_for_state
    wait_for_state( None)
    if _DEBUG: print "util: save_scene_as 5"
    wx.GetApp().set_busy_state(True)
    saved = False
    try:
        if _DEBUG: print "util: save_scene_as enter code_exporter"
        code_exporter( scene, path, True, {'name':sceneName})
        if _DEBUG: print "util: save_scene_as exit code_exporter"
    except:
        if _DEBUG: print "util: save_scene_as 6"        
        show_exception_dialog()
    else:
        if _DEBUG: print "util: save_scene_as 7"        
        sceneDict = get_available_scenes(True)
        if '__Working__' not in path:
            PigDirector.scene.__class__ = sceneDict[sceneName]
        saved = True
        if _DEBUG: print "util: save_scene_as 8"        
    finally:
        if _DEBUG: print "util: save_scene_as 9"                
        wx.GetApp().set_busy_state(False)        
        if PigDirector.scene != oldscene:
            wx.GetApp().set_selection([])
            if _DEBUG: print "util: save_scene_as reset select:", selection
        from pig.editor.EditorState import EditorState
        wait_for_state(EditorState)
        if _DEBUG: print "util: save_scene_as 10"                
        wx.GetApp().refresh()
    if _DEBUG: print "util: save_scene_as 11"                
    if saved:
        return fileName
    else:
        return False
          

def get_scene_errors(showDialog=True):
    """get_scene_errors(showDialog=True)->error string
    
Check the scene for probable user errors. If showDialog is False, returns a list
of errors or None if none found. If showDialog is True, brings up a dialog to
allow the user to ignore the errors. This function checks for unnamed 
archetypes, and multiple archetypes with the same name...
"""
    scene = PigDirector.scene
    errors = []
    if not scene:
        error = "No scene loaded!"
        errors.append(error)
    else:
        archetypeNames = []
        for node in scene.nodes:
            if node.archetype:
                if node.gname:
                    if node.gname in archetypeNames:
                        error = ''.join(["Duplicate archetype name: ",
                                         node.gname])
                        errors.append(error)
                    else:
                        archetypeNames.append(node.gname)
                else:
                    error = ''.join(["Unnamed archetype: class ", 
                                     node.__class__.__name__, " at ",
                                     str(node.position.x), ", ",
                                     str(node.position.y)])
                    errors.append(error)
    if errors:
        if showDialog:
            errorend = ['\nIgnore errors and save (not recommended)?']
            errormsg = '\n'.join(errors + errorend)
            dlg = wx.MessageDialog( wx.GetApp().get_project_frame(), errormsg, 
                                    "Scene Errors",
                                    style = wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_YES:
                return None
            else:
                return errors
        else:
            return errors
    else:
        return None
