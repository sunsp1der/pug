"""wx app for pug"""
import weakref
import os
import traceback
import time
# from dummy_threading import Thread
# import dummy_thread as thread
# import thread
from threading import Thread
from inspect import getsourcefile

import wx

from pug.util import make_name_valid
from pug.CallbackWeakKeyDictionary import CallbackWeakKeyDictionary
from pug.syswx.util import show_exception_dialog
from pug.syswx.pugframe import PugFrame
from pug.syswx.SelectionWindow import SelectionWindow

# TODO: create 'Initializing Pug' window
# TODO: create a link between project closing and app closing

_RECTPREFIX = 'rect_'
_DEBUG = False

class pugApp(wx.App):
    """pugApp: wx.App for the pug system

pugApp((self, projectObject=None, projectObjectName='',
                 projectName='PUG', projectFolder = "" )   

projectObject: the object to show in the initial pug view
projectObjectName: for use in sub-frame titles. If not provided and
    projectObject.gname exists, this will be set to projectObject.gname
projectName: name of the project/title of initial frame.
    If this is not provided and projectObjectName is not "", this will be set
    to projectObjectName 
projectFolder: where file menus start at.  Defaults to current working dir.
"""
    quitting = False
    busyState = False
    setting_selection = False
    progressDialog = None
    initTryCounter = 0
    settings = object()
    projectFrame = None
    def __init__(self, projectObject=None, projectObjectName='',
                 projectName='PUG', projectFolder = "", redirect=False ):
        #wx.PySimpleApp.__init__(self)
        wx.App.__init__(self, redirect=redirect)
        #self.SetExitOnFrameDelete(False)
        
        # global menus
        self.globalMenuDict = {'__order__':[],'__ids__':{}}
        
        # selection manager stuff
        self.selectedObjectDict = CallbackWeakKeyDictionary()
        self.selectedObjectDict.register(self.on_selectedObjectDict_change)
        self.selectionWatcherDict = weakref.WeakKeyDictionary()        
        
        # track frames and objects they view { 'frame':obj(id)}
        self.pugFrameDict = weakref.WeakKeyDictionary()
        self.set_project_folder(projectFolder)
        if projectObject:
            self.start_project(projectObject, projectObjectName,
                          projectName, projectFolder)
    
    def start_project(self, projectObject=None, projectObjectName='',
                 projectName='PUG', projectFolder = "" ):
        if projectObjectName == '' and getattr(projectObject,'gname',None):
            self.projectObjectName = projectObject.gname
        else:
            self.projectObjectName = projectObjectName
        if projectName == 'PUG' and self.projectObjectName:
            self.projectName = projectObjectName
        else:
            self.projectName = projectName
        
        # default save and load folder 
        self.set_project_object(projectObject)        
        self.MainLoop()
        
        
    def set_project_folder(self, projectFolder=None):
        if projectFolder:
            self.projectFolder = os.path.dirname(projectFolder)
        else:
            self.projectFolder = os.getcwd()
                   
    def set_project_object(self, object=None):
        self.projectObject = object
        if not object:
            return
        self.initTryCounter = 1
        self.initProgressDialog = wx.ProgressDialog("Python Universal GUI",
                                            'PUG system initializing...',
                                            parent=None,
                                            maximum=10)
#        self.initProgressDialog.SetSize((400,
#                                         self.initProgressDialog.GetSize()[1]))
        self.initProgressDialog.Bind(wx.EVT_CLOSE, self.abort_init)
        self.initProgressDialog.Update(0)
        self.initProgressDialog.Raise()
        self.initProgressDialog.Show()
        if object:
            self.post_init(object)
            return
        self.finalize_project_object(object)
                    
    def abort_init(self, event=None):
        """Close project while trying to set a project object"""
        self.initProgressDialog.Destroy()
        self.quit()
        self.Destroy()
    
    def post_init(self,object):
        """post_init(self)
Pug will open an object frame when object._isInitialized flag is set. If object 
is not initialized, its _try_initialize() function is run here. This method is
called every second until the object is initialized"""
        if self.quitting:
            return
        if hasattr(object,'_isReady') and not object._isReady:
            error = 'unknown error'
            if hasattr(object,'_try_post_init'):
                error = object._try_post_init()
            if self.initTryCounter:
                # we're only going to do this for 10 tries
                # then we're gonna guess something's broken
                self.initTryCounter += 1
                if self.initProgressDialog:
                    if error:
                        msg = error[3].splitlines()[-1]
                        self.initProgressDialog.Update(self.initTryCounter, msg)
                        self.initProgressDialog.Fit()
                    else:
                        msg = ''.join(['PUG system initializing... tries: ',
                                   str(self.initTryCounter)])
                        self.initProgressDialog.Update(self.initTryCounter, msg)
                    self.initProgressDialog.Raise()
                if self.initTryCounter == 10:
                    self.post_init_failed(error)
                    return
        if not hasattr(object,'_isReady') or object._isReady:        
            msg = 'Opening Project...'
            self.initProgressDialog.Update(9, msg)
            self.initProgressDialog.Raise()
            time.sleep(0.05)
            self.finalize_project_object( object)
        else:
            wx.CallLater(500,self.post_init,object)
            time.sleep(0.3)
            
    def finalize_project_object(self, object):
        if object is None:
            object = self.projectObject
        if not self.projectFrame:
            try:
                frame = PugFrame(obj=object, title=self.projectName, 
                      objectpath=self.projectObjectName) 
            except:
                show_exception_dialog()
            self.set_project_frame(frame)
        self.register_selection_watcher(object)
        if self.initProgressDialog:
            self.initProgressDialog.Destroy()
        self.SetExitOnFrameDelete(True)
        self.projectFrame.Raise()
            
    def set_project_frame(self,  frame):
        self.projectFrame = frame 
        self.projectFrame.Bind(wx.EVT_CLOSE, self._evt_project_frame_close, 
                               id=self.projectFrame.GetId()) 
        
    def get_project_frame(self):
        return self.projectFrame
            
    def post_init_failed(self, error):
        try:
            self.projectObject.quit()
        except:
            pass
        msg = ''.join(['pug.App.post_init error:\n',error[3]])
        print msg
        print
        raise Exception(msg)

    def _evt_project_frame_close(self, event = None):
        if (event and not event.CanVeto()) or self.quitting:
            if event:
                event.Skip()
            return
        if hasattr(self.projectObject, "_pre_quit_func"):
            doquit = self.projectObject._pre_quit_func( event)
            if not doquit:
                return
        else:
            dlg = wx.MessageDialog(self.projectFrame,
                           "Close all windows and exit project?",
                           'Project Frame Closed', 
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        #TODO: would be nice if the dlg could be forced above other apps
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return
        self.quit()
        if event:
            event.Skip()

    def quit(self, event = None):
        if self.quitting:
            if event:
                event.Skip()
            return
        self.quitting = True
        try:
            projectObject = self.projectObject
            if hasattr(projectObject, '_on_pug_quit'):
                projectObject._on_pug_quit()
        except:
            print "Exception during _on_pug_quit"
            print traceback.format_exc()
        for pugframe in self.pugFrameDict:
            if pugframe:
                pugframe.Close()
        self.Exit()
        
    def pugframe_viewing(self, frame, object):
        """pugframe_viewing(frame)

Notify the app that a PugFrame has opened, so that it can track object views.
frame: the frame that is being opened
object: the object being viewed. Alternatively, this can be a string identifying
    the pugframe.
"""
#        if self.progressDialog and frame.object == self.projectObject:
#            self.progressDialog.Destroy()
#            self.progressDialog = None
        if object is None:
            objList = []
        else:
            objList = [id(object)]
        if _DEBUG: print "app.pugframe_viewing: ",object, objList
        if self.pugFrameDict.get(frame, False):
            self.pugFrameDict[frame]+=objList
        else:
            self.pugFrameDict[frame]= objList
        if _DEBUG: print "   app.pugframe_viewing complete"
            
    def pugframe_stopped_viewing(self, frame, object):
        if frame in self.pugFrameDict:
            if object in self.pugFrameDict[frame]:
                self.pugFrameDict[frame].remove(object)
            
    def get_object_pugframe(self, object):
        """get_object_pugframe(object)
        
Return the PugFrame currently viewing 'object', or None if not found.
"""
        searchid = id(object)
        pugframe = None
        if _DEBUG: print "app.get_object_pugframe: ",object,searchid,\
                            "\n Dict:", self.pugFrameDict.data
        for frame, objlist in self.pugFrameDict.iteritems():
            if frame and searchid in objlist:
                pugframe = frame
        return pugframe
        
    def show_object_pugframe(self, object):
        """show_object_pugframe(object)
        
Raise the pugframe viewing 'object'. If it exists return the frame... otherwise, 
return None. If the frame has an 'on_show_object' function, it will be called
with object as an argument
"""
        frame = self.get_object_pugframe(object)
        if frame:
            if hasattr(frame, 'on_show_object'):
                frame.on_show_object(object)
        return frame
    
    def show_selection_frames(self):
        """show_selection_frames(object)
        
Raise the apps current selection frames. If any exist, return a list of them.
Otherwise, return None. 
"""
        frameList = []
        if self.selectionWatcherDict:
            for watcher in self.selectionWatcherDict:
                if isinstance(watcher, PugFrame):
                    watcher.Show()
                    watcher.Raise()
                    frameList.append(watcher)
            return frameList
        else:
            return None
    
    def set_selection(self, selection=[], skipObj=None):
        """set_selection( selection=[], skipObj=None)
        
selection: a list of objects that are currently selected in the project. 
skipObj: this object will not get a callback 
    (convenience to prevent infinite loop)

Set the interface's selectedObjectDict. These objects can be viewed in a PugWindow 
by calling the open_selection_frame method. Selection is tracked in a set, so 
duplicates will be automatically eliminated.
"""
        if _DEBUG: print "app.set_selection:",selection
        if _DEBUG: print "    old selection:",self.selectedObjectDict.keys()
        if self.setting_selection:
            return
        self.setting_selection = True
        selectSet = set(selection)
        if selectSet != set(self.selectedObjectDict.keys()):
            self.selectedObjectDict.clear()
            for item in selection:
                try:
                    ref = weakref.ref(item)
                except:
                    msg = ''.join([
                            "PugApp.set_selection can't create ref to:",
                            item])
                    raise ValueError(msg) 
                self.selectedObjectDict[item] = ref
        for obj in self.selectionWatcherDict:
            if obj == skipObj:
                continue
            if hasattr(obj, 'on_set_selection'):
                obj.on_set_selection( self.selectedObjectDict)
        self.setting_selection = False
        
    def get_selection(self):
        "get_selection() -> selectedObjectDict. WeakKeyDictionary {obj:ref,...}"
        return self.selectedObjectDict.copy()
        
    def on_selectedObjectDict_change(self, dict, func_name, arg1, arg2):
        if self.setting_selection:
            return
        #wx.CallAfter(self.set_selection, dict.keys())
            
    def open_selection_frame(self):
        """open_selection_frame()

Open a SelectionFrame, or if one exists AND control is not being held down, 
bring it to the top. For arguments, see the doc for PugFrame.  
Selection frames display pug views of the objects in self.selectedObjectDict. 
The selectedObjectDict can be changed using the set_selection method.
"""
        if wx.GetKeyState(wx.WXK_CONTROL) or not self.show_selection_frames():
            frame = PugFrame( name="Selection")
            frame.set_pugwindow(SelectionWindow(frame))
        else:
            frame = None

    def selection_refresh(self):
        """selection_refresh()
        
Send a on_selection_refresh message to all objects in the selectionWatcherDict.
This will not be called automatically... only when requested by the user.
"""
        for obj in self.selectionWatcherDict:
            if hasattr(obj, 'on_selection_refresh'):
                obj.on_selection_refresh()

    def register_selection_watcher(self, obj):
        """register_selection_watcher(obj)
        
Register an object to receive 'on_set_selection( selectedObjectDict)' callback 
when the App's selectedObjectDict changes. selectedObjectDict is a dict of 
obj:reference of selected objects. Registered objects will also receive an 
'on_selection_refresh' callback when a selected object changes (must be 
implemented by user). Project object will automatically be registered if it has 
an attribute called on_set_selection.
"""
        self.selectionWatcherDict[obj] = id(obj)
        
    def add_global_menu(self, name, entryList):
        """add_global_menu(name, entryList) 
        
Add a global menu to be placed on all pugframes. 

name: menu name. Do not use __ids__ or __order__ as names
entryList: a list of entries in this form: 
   [command name, function info, tooltip (optional)]
   OR
   ["*DIVIDER*"] for menu divider
   command name: name or name\tHOTKEY with HOTKEY like Shift+Ctrl+A
   function info: function to run or [function, args, kwargs]
"""
        order = self.globalMenuDict['__order__']
        if name in order:
            order.remove(name)
        order.append(name)
        self.globalMenuDict[name] = entryList
        
    def remove_global_menu(self, name):
        """remove_global_menu(name): remove the named menu"""
        self.globalMenuDict['__order__'].remove(name)
        return self.globalMenuDict.pop(name,None)

    def append_global_menus(self, menubar):
        """append_global_menus( menubar)

menubar: the wx.MenuBar to add the global menus to
"""
        menuList = self.globalMenuDict['__order__']
        for menuName in menuList:
            menu = wx.Menu()
            menubar.Append(menu=menu, title=menuName)
            menuEntries = self.globalMenuDict.get(menuName, [])
            for entry in menuEntries:
                if entry == ["*DIVIDER*"]:
                    menu.AppendSeparator()
                    continue
                id = wx.NewId()
                name = entry[0]
                func = entry[1]
                if len(entry) > 2:
                    tooltip = entry[2]
                else:
                    tooltip = name
                self.globalMenuDict['__ids__'][id] = func
                menu.Append(help=tooltip, id=id, text=name)
                self.Bind(wx.EVT_MENU, self._evt_on_global_menu, id=id)
                
    def _evt_on_global_menu(self, event):
        info = self.globalMenuDict['__ids__'][event.Id]
        if type(info) is list:
            if len(info) == 1: 
                info[1] = ()
            if len(info) == 2:
                info[2] = {}
            info[0](*info[1], **info[2])
        else:
            info()
        
    def set_busy_state(self, On=True):
        """set_busy_state(On=True)

If 'On', start busy cursor and send on_set_busy_state(True) callback to project 
object. If not 'On', end busy cursor and send on_set_busy_state(False) callback.
"""
        if On and not self.busyState:
            wx.BeginBusyCursor()
        elif not On and self.busyState:
            wx.EndBusyCursor()
        else:
            return
        self.busyState = On
        if hasattr(self.projectObject, 'on_set_busy_state'):
            self.projectObject.on_set_busy_state(On)
            
    def set_pug_settings(self, settingsObj):
        """set_pug_settings(settingsObj)
        
settingsObj: a class with values like those created in create_frame_settings.
"""        
        self.settings = settingsObj
            
    def getrect_setting_name(self, frame):
        return make_name_valid(''.join([_RECTPREFIX,frame.Name]))
            
    def create_frame_settings(self, settingsObj=None):
        """create_frame_settings(settingsObj=None)->setting data class
        
settingsObj: any frame settings members will be replaced
"""
        class frame_settings():
            pass
        for frame in wx.GetTopLevelWindows():
            # setting entry like: framename_rect = (x, y, width, height)
            if not frame.Name:
                continue
            name = self.getrect_setting_name(frame)
            data = (frame.Position[0], frame.Position[1], 
                    frame.Size[0], frame.Size[1])
            setattr(frame_settings, name, data)
        if settingsObj:
            # erase old rects
            keys = settingsObj.__dict__.keys()
            for attr in keys:
                if attr.startswith(_RECTPREFIX):
                    delattr( settingsObj, attr) 
            # add new rects
            for attr, data in frame_settings.__dict__.iteritems():
                if attr.startswith(_RECTPREFIX):
                    setattr(settingsObj,attr, data)
            return settingsObj
        else:
            return frame_settings            
            
    def get_default_pos(self, frame):
        name = self.getrect_setting_name(frame)
        return getattr(self.settings, name, None)
            
    def raise_all_frames(self):
        windows = wx.GetTopLevelWindows()
        win = None
        for frame in windows:
            if frame.IsActive():
                win = frame
        for frame in windows:
            if frame != win and frame.IsShown():
                if frame.IsIconized():
                    frame.Iconize(False)
                frame.Raise()
        if win:
            win.Raise()
            
    def refresh(self, event=None):
        windows = wx.GetTopLevelWindows()
        for frame in windows:
            if hasattr( frame, 'refresh'):
                frame.refresh()            
            
    def apply(self, event=None):
        windows = wx.GetTopLevelWindows()
        for frame in windows:
            if hasattr( frame, 'apply'):
                frame.apply()