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
from pug.syswx.util import show_exception_dialog
from pug.syswx.pugframe import PugFrame
from pug.syswx.SelectionWindow import SelectionWindow

# TODO: create 'Initializing Pug' window
# TODO: create a link between project closing and app closing

_RECTPREFIX = 'rect_'

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
                 projectName='PUG', projectFolder = "" ):
        #wx.PySimpleApp.__init__(self)
        wx.App.__init__(self)
        #self.SetExitOnFrameDelete(False)
        
        # global menus
        self.globalMenuDict = {'__order__':[],'__ids__':{}}
        
        # selection manager stuff
        self.selectedRefSet = set()
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
        time.sleep(0.05)
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
            time.sleep(0.1)
            
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
            
    def post_init_failed(self, error):
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
        
    def pugframe_opened(self, frame, object=None):
        """pugframe_opened(frame)

Notify the app that a PugFrame has opened, so that it can track object views.
frame: the frame that is being opened
object: the object being viewed. Alternatively, this can be a string identifying
    the pugframe.
"""
#        if self.progressDialog and frame.object == self.projectObject:
#            self.progressDialog.Destroy()
#            self.progressDialog = None
        if object is None:
            try:
                objId = id(frame.objectRef())
            except:
                objId = id(frame.object)
        else:
            objId = id(object)
        if self.pugFrameDict.get(frame, False):
            self.pugFrameDict[frame].append( objId)
        else:
            self.pugFrameDict[frame]= [objId]
            
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
        for frame, objlist in self.pugFrameDict.iteritems():
            if frame and searchid in objlist:
                pugframe = frame
        return pugframe
        
    def show_object_pugframe(self, object):
        """show_object_pugframe(object)
        
Raise the pugframe viewing 'object'. If it exists return the frame... otherwise, 
return None. 
"""
        frame = self.get_object_pugframe(object)
        if frame:
            frame.Show()
            frame.Raise()
            frame.show_object(object)
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
    
    def set_selection(self, selectList=[], skipObj=None):
        """set_selection( selectList=[], skipObj=None)
        
selectList: a list of objects that are currently selected in the project. 
skipObj: this object will not get a callback 
    (convenience to prevent infinite loop)

Set the interface's selectedRefSet. These objects can be viewed in a PugWindow 
by calling the open_selection_frame method. Selection is tracked in a set, so 
duplicates will be automatically eliminated.
"""
        if self.setting_selection:
            return
        self.setting_selection = True
        self.selectedRefSet.clear()
        for item in selectList:
            if isinstance(item, weakref.ReferenceType):
                self.selectedRefSet.add(item)
            else:
                self.selectedRefSet.add( weakref.ref(item))
        for obj in self.selectionWatcherDict:
            if obj == skipObj:
                continue
            if hasattr(obj, 'on_set_selection'):
                obj.on_set_selection( self.selectedRefSet)
        self.setting_selection = False
            
    def open_selection_frame(self):
        """open_selection_frame()

Open a SelectionFrame, or if one exists AND control is not being held down, 
bring it to the top. For arguments, see the doc for PugFrame.  
Selection frames display pug views of the objects in self.selectedRefSet. The 
selectedRefSet can be changed using the set_selection method.
"""
        if not self.show_selection_frames() or wx.GetKeyState(wx.WXK_CONTROL):
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
        
Register an object to receive 'on_set_selection( selectedRefSet)' callback 
when the App's selectedRefSet changes. selectedRefSet is a set of references to
selected objects. Registered objects will also receive a 'on_selection_refresh' 
callback when a selected object changes (must be implemented by user). 
Project object will automatically be registered if it has an attribute called 
on_set_selection.
"""
        self.selectionWatcherDict[obj] = id(obj)
        
    def add_global_menu(self, name, entryList):
        """add_global_menu(name, entryList) 
        
Add a global menu to be placed on all pugframes. 

name: menu name. Do not use __ids__ or __order__ as names
entryList: a list of entries in this form: 
   [command name, function to be run, tooltip (optional)]
   For hotkeys set command name to: NAME\tHOTKEY with HOTKEY like Shift+Ctrl+A
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
            newMenu = wx.Menu()
            menubar.Append(menu=newMenu, title=menuName)
            menuEntries = self.globalMenuDict.get(menuName, [])
            for entry in menuEntries:
                id = wx.NewId()
                name = entry[0]
                func = entry[1]
                if len(entry) > 2:
                    tooltip = entry[2]
                else:
                    tooltip = name
                self.globalMenuDict['__ids__'][id] = func
                newMenu.Append(help=tooltip, id=id, text=name)
                self.Bind(wx.EVT_MENU, self._evt_on_global_menu, id=id)
                
    def _evt_on_global_menu(self, event):
        func = self.globalMenuDict['__ids__'][event.Id]
        func()
        
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
                frame.Raise()
        if win:
            win.Raise()
            
    def apply_all(self, event=None):
        windows = wx.GetTopLevelWindows()
        for frame in windows:
            if hasattr( frame, 'apply'):
                frame.apply()