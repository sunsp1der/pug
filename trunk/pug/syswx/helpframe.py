from inspect import *
from sys import exc_info
import weakref

import wx
import wx.lib.scrolledpanel as scrolled

from pug.syswx.pugbutton import PugButton
from pug.syswx.wxconstants import *

# TODO: make showPugButton work for empty list

class HelpFrame(wx.Frame):
    """HelpFrame(...): Return a frame showing basic info for 'object'. 
    
(object, parent=none,  attribute='', objectPath='', showPugButton = True) 

    parent is the frame's parent
    title is the frame's title. Generally, this should be the object's name
    showPugButton': include a button for opening a pugFrame for the object
"""
    def __init__(self, object, parent=None, attribute='', objectPath='', 
                 showPugButton=False):
        wx.Frame.__init__(self, parent, -1, title = 'Help')
        self.scrollPanel = scrolled.ScrolledPanel(self, -1)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        if parent:
            # button for retyping object
            bmp = wx.ArtProvider.GetBitmap(wx.ART_REDO, 
                                           wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
            tooltip = "Change object's type"
            retypebutton = wx.BitmapButton(self, 
                              size=WX_BUTTON_SIZE,
                              bitmap = bmp
                              )
            retypebutton.SetToolTipString(tooltip)
            retypebutton.Bind(wx.EVT_BUTTON, self.retype_object)
            self.ButtonSizer.Add(retypebutton,0)            
        if showPugButton:
            # button for viewing object in pug
            pugbutton = PugButton(self, object, True, objectPath)
            self.ButtonSizer.Add(pugbutton, 0)
        self.Sizer.AddSizer(self.ButtonSizer, 0, wx.ALIGN_RIGHT)
        self.Sizer.Add(self.scrollPanel, 1, flag = wx.EXPAND)
        self.flexGridSizer = None
        self.CreateStatusBar()
        self.set_object(object, objectPath, showPugButton)
        self.attribute = attribute
    
    def retype_object(self, Event = None):
        """open a dialog to change object's type"""
        msg = ''.join(["Enter a new value for this attribute.\n",
                       "Use #None# to set the value to None.\n",
                       "Equivalent to the command:\n",
                       self.objectPath," = <Entry>"])
        dlg = wx.TextEntryDialog(self, msg, "Change Object Type")
        if dlg.ShowModal() == wx.ID_OK:
            parentobject = self.GetParent().object
            value = dlg.GetValue()
            if value == "#None#":
                val = None
            else:
                try:
                    val = eval(value,{},{})
                except:
                    val = value            
            if isinstance(val, basestring):
                command = \
                "setattr(parentobject,self.attribute,val)"
            else:
                command = ''.join(["parentobject.", 
                               self.attribute, " = ", str(val)])
            try:
                exec(command)
            except:
                err = wx.MessageDialog(self, str(exc_info()[0]), 
                     exc_info()[1].__class__.__name__,
                     wx.ICON_ERROR | wx.OK, dlg.Position
                     )
                err.ShowModal()
                err.Destroy()
            else:
                self.GetParent().create_puglist()
                self.Close()
        
    def set_object(self, object, objectPath = None, showPugButton = False):
        self.objectPath = objectPath
        self.object = object        
        self.SetTitle(' - '.join(['Help', objectPath]))
        
        if self.flexGridSizer:
            self.flexGridSizer.Clear(True)
            self.flexGridSizer.Destroy()
            
        info = []
        doc = getdoc(object)
        module = getmodule(object)        
        builtin = module and module.__name__ == '__builtin__'
        if hasattr(object,'__class__'):
            isInstance = True
            classmodule = getmodule(object.__class__)
            if classmodule and classmodule.__name__ == '__builtin__':
                builtin = True
        if isInstance:
            mro = getmro(object.__class__)
        elif isclass(object):
            mro = getmro(object)
        else:
            mro = None
        if objectPath:
            info += ['Object:',objectPath]
        if doc and (isroutine(object) or not builtin):
            info += ["Doc:",doc]
        info += ["Value:", repr(object)]
        info += ["Type:", type(object).__name__]
        if module:
            info += ["Module:", str(module)]
        if mro and not builtin and not isroutine(object):
            info +=["MRO:",str(mro)]
            
        rows = int(len(info)*0.5)
        flex = self.scrollPanel.Sizer = wx.FlexGridSizer(rows,2,8,3)
        flex.AddGrowableCol(1)
        for i in range(rows):
            flex.AddGrowableRow(i)
        flex.SetFlexibleDirection(wx.BOTH)  
        label = True      
        for data in info:
            control = wx.StaticText(self.scrollPanel, -1, label = data)
            flex.Add(control)
            if label: 
                control.SetForegroundColour((150,150,150))

            label = not label
                
        self.flexGridSizer = flex
                     
        self.SetMinSize((150,60))
        self.SetClientSize((flex.MinSize[0]+self.Sizer.MinSize[0],
                            flex.MinSize[1]+self.Sizer.MinSize[1]))
        width, height = (self.Size[0]+20, self.Size[1])
        maxheight = height
        maxwidth = width
        if height > 300:
            height = 300
        if width > 600:
            width = 600
        self.SetSize((width, height))
        self.SetMaxSize((maxwidth, maxheight))
        self.scrollPanel.SetupScrolling()
        
