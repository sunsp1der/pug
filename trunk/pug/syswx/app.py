"""wx app for pug"""
import weakref
import os
# from dummy_threading import Thread
# import dummy_thread as thread
# import thread
from threading import Thread
from inspect import getsourcefile

import wx

from pug.syswx.pugframe import PugFrame

# TODO: create 'Initializing Pug' window
# TODO: create a link between project closing and app closing

class pugApp(wx.PySimpleApp):
    """pugApp: wx.App for the pug system
    
arguments:
projectObject=None: the object to show in the initial pug view
projectObjectName="": for use in sub-frame titles. If not provided and
    projectObject.gname exists, this will be set to projectObject.gname
projectName="PUG": name of the project/title of initial frame.
    If this is not provided and projectObjectName is not "", this will be set
    to projectObjectName 
projectFolder="": where file menus start at.  Defaults to current working dir.
"""
    def __init__(self, projectObject=None, projectObjectName='',
                 projectName='PUG', projectFolder = "" ):
        wx.PySimpleApp.__init__(self)
        self.SetExitOnFrameDelete(False)
        self.quitting = False
        self.progressDialog = None
        self.initTryCounter = 0 #so we don't loop on post_init_forever
        
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

#        thread.start_new_thread(self.MainLoop,())
#        thread = PugAppThread(app=self)
#        thread.start()
        self.MainLoop()
        
        
    def set_project_folder(self, projectFolder=None):
        if projectFolder:
            self.projectFolder = os.path.dirname(projectFolder)
        else:
            self.projectFolder = os.getcwd()
                   
    def set_project_object(self, object):
        self.projectObject = object
        if not object:
            return
        self.initTryCounter = 1
        self.initProgressDialog = wx.ProgressDialog("Python Universal GUI",
                                            'PUG system initializing...',
                                            parent=None,
                                            style=wx.PD_ELAPSED_TIME,
                                            maximum=23)
        self.initProgressDialog.SetSize((400,
                                         self.initProgressDialog.GetSize()[1]))
        self.initProgressDialog.Bind(wx.EVT_CLOSE, self.abort_init)
        self.initProgressDialog.Update(0)
        if object:
            self.post_init(object)
                    
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
                exc = object._try_post_init()
                if exc:
                    error = ''.join([repr(exc[1])])
            if self.initTryCounter:
                # we're only going to do this for 10 tries
                # then we're gonna guess something's broken
                self.initTryCounter += 1
                if self.initTryCounter == 23:
                    if self.initProgressDialog:
                        self.initProgressDialog.Update(self.initTryCounter, 
                                                       error)
                    self.post_init_failed(error)
                    return
                if self.initProgressDialog:
                    msg = ''.join(['PUG system initializing... tries: ',
                                   str(self.initTryCounter)])
                    self.initProgressDialog.Update(self.initTryCounter, msg)
        if not hasattr(object,'_isReady') or object._isReady:        
            msg = 'PUG system initialized...'
            self.initProgressDialog.Update(22, msg)
            self.open_project_frame(object) 
            self.initTryCounter = 1
            if self.initProgressDialog:
                self.initProgressDialog.Destroy()
            self.SetExitOnFrameDelete(True)
            self.projectFrame.Raise()
        else:
            wx.CallLater(500,self.post_init,object)
            
    def open_project_frame(self, object = None):
        if object is None:
            object = self.projectObject
        self.projectFrame = PugFrame(obj=object, title=self.projectName, 
                      objectpath=self.projectObjectName) 
        self.projectFrame.Bind(wx.EVT_CLOSE, self._evt_project_frame_close, 
                               id=self.projectFrame.GetId()) 
            
    def post_init_failed(self, error):
        msg = ''.join(['pug.App.post_init error:',error])
        print msg
        raise Exception(msg)

    def _evt_project_frame_close(self, event = None):
        if self.quitting:
            event.Skip()
            return
        if self.projectObject in self.projectFrame.get_object_list():
            dlg = wx.MessageDialog(self.projectFrame,
                               "Close all windows and exit project?",
                               'Project Frame Closed', 
                               wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() != wx.ID_YES:
                return
        self.quit()
        if event:
            event.Skip()

    def quit(self, event = None):
        if self.quitting:
            event.Skip()
            return
        self.quitting = True
        for pugframe in self.pugFrameDict:
            if pugframe:
                pugframe.Close()
        try:
            projectObject = self.projectObject
            if hasattr(projectObject, '_on_pug_quit'):
                projectObject._on_pug_quit()
        except:
            pass
        
    def pugframe_opened(self, frame, object=None):
        """pugframe_opened(frame)

Notify the app that a PugFrame has opened, so that it can track object views
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
            
    def get_object_pugframe(self, object):
        """get_object_pugframe(object)
        
Return the PugFrame currently viewing 'object', or None if not found.
"""
        searchid = id(object)
        for frame, objlist in self.pugFrameDict.iteritems():
            if frame and searchid in objlist:
                return frame
        return None
        
    def show_object_pugframe(self, object):
        """show_pugframe(object)
        
Raise the pugframe viewing 'object'. If it exists return the frame... otherwise, 
return None. This has the special functionality of ALWAYS returning None if the
control key is currently pressed. This has the effect of allowing the user to 
open 2 windows for the same object. 
"""
        frame = self.get_object_pugframe(object)
        if frame:
            frame.Show()
            frame.Raise()
            frame.show_object(object)
        return frame
#
class PugAppThread(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self)
        self.app = kwargs['app']
    def run(self):
        self.app.MainLoop()
        