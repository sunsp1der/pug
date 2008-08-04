import re
import weakref

import wx

from pug.syswx.wxconstants import *

# TODO: I think myPugFrame could be removed if I can figure out how to get
#        parent's top level window

class PugButton(wx.BitmapButton):
    """A button that opens a pug frame, either in the current or in a new frame
    
PugButton(parent, targetObject, objectName="the object", doOpenNew=True, 
    myPugFrame=None, size=None, text=None)
    
parent: parent control
targetObject: clicking the button shows a pugView of this object
objectName: a text name of the object
doOpenNew: if True, button opens a new pug view of the object, otherwise it
    changes the current pugframe to show the object
myPugFrame: if doOpenNew is False... the frame to show the object view
targetObjectFn: a function that returns a targetObject, as an alternative to
    setting the targetObject explicitly
size: the button size
"""
    targetObjectRef = None
    def __init__(self, parent, targetObject=None, doOpenNew=True, 
                 objectName="object", myPugFrame=None, 
                 targetObjectFn=None, size=None):
        if doOpenNew is False and not myPugFrame:
            raise(Exception(
                "PugButton: must provide a PugFrame when doOpenNew is false"))
        if size is None:
            size = WX_BUTTON_SIZE
        self.targetObjectFn = targetObjectFn
        if (doOpenNew):
            bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, 
                                           wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
            tooltip = ''.join(["View '",objectName,"' in a new window"])
            fn = self.on_new_view_button
        else:
            bmp = wx.ArtProvider.GetBitmap(wx.ART_FIND, 
                                            wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
            tooltip = ''.join(["View '",objectName,"' in this window"])
            fn = self.on_view_button                
        wx.BitmapButton.__init__(self, parent=parent, size=size, bitmap=bmp)
        self.SetToolTipString(tooltip)
        self.Bind(wx.EVT_BUTTON, fn, self)   
        if targetObject:
            self.set_object(targetObject, objectName, myPugFrame)

        # keep the pug function around for button pressing
        # don't know if this is the right way to do it
        from pug.syswx.pugframe import PugFrame
        self.PugFrame = PugFrame

    def set_object(self, targetObject, objectName=None, myPugFrame=None):
        if not self.targetObjectFn:
            try:
                targetObjectRef = weakref.ref(targetObject)
            except:
                self.targetObject = targetObject
                def targetObjectRef():
                    return targetObject
            self.targetObjectRef = targetObjectRef
        if objectName:
            self.objectName = objectName 
        if myPugFrame:
            self.myPugFrame = myPugFrame
            
    def on_view_button(self, event = None):
        obj = self.get_obj()
        if obj:
            self.myPugFrame.set_object(obj, objectpath=self._getNewPath())
        
    def on_new_view_button(self, event = None):  
        obj = self.get_obj()
        if obj:
            self.PugFrame(obj=obj, objectpath=self._getNewPath())

    def get_obj(self):
        if self.targetObjectFn:
            obj = self.targetObjectFn()
        else:
            if self.targetObjectRef and self.targetObjectRef() is None:
                return None
            obj = self.targetObjectRef()
        app = wx.GetApp()
        if not app.show_object_pugframe(obj) or wx.GetKeyState(wx.WXK_CONTROL):
            return obj
        else:
            return None

    def _getNewPath(self):
        if self.myPugFrame and self.myPugFrame.objectPath != None:
            if self.myPugFrame.objectPath == "":
                pugPath = self.objectName
            else:
                pugPath = ''.join([self.myPugFrame.objectPath,'.',
                                   self.objectName])
            return pugPath
        elif self.objectName != 'the object':
            return self.objectName
        else:
            return None