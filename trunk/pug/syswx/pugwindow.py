#Boa:Frame:PugFrame
"""The basic pug display window

This is generally meant to be created by the pug function. You can send the 
object to be viewed as an argument on creation of the window."""
#some code looks a little mumbo-jumboey because it was made by BOA

# TODO: intercept tabbing stuff with EVT_NAVIGATION_KEY - apply/skip buttons
# TODO: apply when a control loses focus
# TODO: scroll to active control

# TODO: provide interface for creating attribute
# TODO: menu option to go to file where this is defined
# TODO: send puglist a specific list of attributes
# TODO: breakout PugListWindow into its own control derived from splitWindow
# TODO: allow personalized toolbars
# TODO: put all settings in menu

import re
import os.path
from weakref import ref, proxy, ProxyTypes
from sys import exc_info

import wx
import wx.lib

from pug.puglist import create_raw_puglist, create_template_puglist
from pug.util import pugSave, pugLoad, get_simple_name
from pug.constants import *
from pug.syswx.helpframe import HelpFrame
from pug.syswx.wxconstants import *
from pug.templatemanager import get_template_info
from pug.code_storage import code_export

#DEBUG
import sys

class PugWindow(wx.ScrolledWindow):
    """A scrolled window that holds a Python Universal GUI
    
PugWindow(self, parent, obj=None, objectpath="object", title="", show=True)
    parent: parent window
    obj: the object to view
    title: the frame title. if not provided, set_object will create one
    objectpath: relative name e.g. 'mygame.scene.player'
This window also holds members toolBar and menuBar, which allows a frame that
holds multiple PugWindows in tabbed (or other) form.
"""
    
    object = None # proxy of object being viewed
    objectRef = None # a reference to actual object
    shortPath = '' # a simple name for the object being viewed
    objectPath = '' # a longer programmatic path... parent.child.grandchild
    title = ''
    _helpFrame =  None # currently open help frame
    _auto_refresh_timer = None # timer object that refreshes frame
    _doingApply = False # currently in the middle of an apply all
    def __init__(self, parent, obj=None, objectpath="unknown", title=""):        
        self.hasSavedAs = {} # save/export event.Id: (folder, filename)
        self.pugList = [] # list of pug attribute guis describing object
        self.settings = {} # various display settings
        self._settingWidgets = {} # internal list of setting control widgets
        self._viewDict = {}
        app = wx.GetApp()
        #attributes
        self.objectPath = objectpath
        self.defaultFolder = app.projectFolder
        #windows
        wx.ScrolledWindow.__init__(self, parent=parent, pos=wx.Point(0, 0),
              size=WX_PUGFRAME_DEFAULT_SIZE, style=wx.HSCROLL | wx.VSCROLL)
        self.SetScrollRate(1,5)
        self.pugSizer = wx.GridBagSizer()
        self.SetSizer(self.pugSizer)
        self._init_ctrls(parent) #BOA STUFF
        #events
#        self.Bind(wx.EVT_CLOSE, self._evt_on_close)
#        self.Bind(wx.EVT_KILL_FOCUS, self._evt_kill_focus)
        #set up actual object gui
        if obj:
            self.set_object(obj, objectpath, title)     
        else:
            app.pugframe_opened(self.GetParent(), "Empty")                     
                    
    def get_optimal_size(self):
        size = self.pugSizer.CalcMin()
        if self.pugSizer.GetColWidths():
            # double the label width
            niceWidth = self.pugSizer.GetColWidths()[0]*2 
            if size[0] < niceWidth:
                size = (niceWidth,size[1])
        return size
        
    def set_object(self, obj, objectpath="unknown", title=None):
        if self.objectRef and obj and obj is self.objectRef():
            self.display_puglist()
            return
        wx.BeginBusyCursor()
        self.Hide()
        self.shortPath = get_simple_name(obj, objectpath)
        self.defaultFilename = self.shortPath
        if objectpath == "unknown":
            self.objectPath = self.shortPath
        else:
            self.objectPath = objectpath
        if not title:
            #set up title
            title = self.shortPath
            if self.shortPath != self.objectPath:                
                if self.objectPath:
                    title = ''.join([title, ' (',self.objectPath,')'])
        self.title = title
        
        if not obj:
            self.objectRef = None
            self.object = obj
            self.pugList = []
            self.pugSizer.Clear(True)
            self.display_message("No object")
        else:
            wx.GetApp().pugframe_opened(self.GetParent(),obj)             
            try:
                self.objectRef = ref(obj)
                obj = proxy(obj, self._schedule_object_deleted)
            except:
                def objectRef():
                    return obj
                self.objectRef = objectRef
            self.object = obj
            self._init_viewMenu_Items(self.viewMenu)
            self._init_fileMenu_Items(self.fileMenu)
            self.create_puglist()
            # hack to make scrollbars refresh
            parent = self.GetParent()
            size = parent.GetSize()
            parent.SetSize((1,1))
            parent.SetSize(size)
            # end hack
        self.Show()                   
        wx.EndBusyCursor()        

    def _schedule_object_deleted(self=None, obj=None):
        wx.CallAfter(self._object_deleted, obj)
    def _object_deleted(self, obj=None):
        title = self.title
        self.set_object(None)
        self.display_message(''.join(['Deleted: ', title]))
        parent = self.GetParent()
        if hasattr(parent, 'on_view_object_deleted'):
            parent.on_view_object_deleted( self, obj)
            
    def display_message(self, message):
        """display_message( message)
        
Set the PugWindow to display a simple text message rather than view an object.
To return to object view, call display_puglist().
"""
        sizer = self.pugSizer
        sizer.ShowItems( False)
        sizer.Clear(False)
        self.reset_sizer()
        text = wx.StaticText( self, label = message)
        sizer.Add(text,(0,0), flag = wx.ALIGN_CENTER)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)       
        sizer.Layout()
        
    def reset_sizer(self):
        sizer = self.pugSizer
        rows = range(sizer.GetRows())
        for row in rows:
            sizer.RemoveGrowableRow(row)
        cols = range(sizer.GetCols())
        for col in cols:
            sizer.RemoveGrowableCol(col)
        sizer.SetRows(0)
        sizer.SetCols(0)

    def create_puglist(self):
        wx.BeginBusyCursor()
        self.Freeze()
        filterUnderscore = 0
        if self.settings['hide_1_underscore']:
            filterUnderscore = 1
        elif self.settings['hide_2_underscore']:
            filterUnderscore = 2
        if not self._currentView:
            self._currentView = self._defaultView
        self.template = None
        if self._currentView == 'Raw':
            self.pugList = create_raw_puglist(self.object, self, None, 
                                              filterUnderscore)
        elif self._currentView == 'Raw Data':
            self.pugList = create_raw_puglist(self.object, self, 
                                              ['Default', 'Objects'],
                                              filterUnderscore)
        elif self._currentView == 'Raw Methods':
            self.pugList = create_raw_puglist(self.object, self,['Routine'],
                                              filterUnderscore)
        else:
            template = self._currentView
            self.template = template
            self.pugList = create_template_puglist(self.object, self, template,
                                                   filterUnderscore=0)
            self.SetSize(wx.Size(template['size'][0], 
                                 template['size'][1]))
            if template.get('force_persist'):
                self.persist = self.objectRef()
            else:
                self.persist = None
        self.display_puglist()
        self.Thaw()
        wx.EndBusyCursor()

    def display_puglist(self):
        wx.BeginBusyCursor()    
        self.Freeze()
        if self.object:
            if self.pugList:         
                sizer = self.pugSizer
                #clear pugList
                sizer.Clear(True)
                self.reset_sizer()
                #set up attributeguis
                # self.labelWidth = 0 # USED TO BE FOR SASH ADJUST
                row = 0
                for item in self.pugList:
                    try:
                        item.refresh()
                    except:
                        item.label.Hide()
                        item.control.Hide()
                        pass
                    else:
                        if item._aguidata.get('control_only', False):
                            # span across label and control
                            sizer.Add(item.control, (row,0), (1,2),
                                      flag=wx.EXPAND | wx.SOUTH, 
                                      border=WX_PUGLIST_YSPACER)
                            item.label.Hide()
                            item.control.Show()
                        else:
                            sizer.Add(item.label, (row,0), 
                                      flag=wx.EXPAND | wx.SOUTH, 
                                      border=WX_PUGLIST_YSPACER)
                            sizer.Add(item.control, (row,1), 
                                      flag=wx.EXPAND | wx.SOUTH, 
                                      border=WX_PUGLIST_YSPACER)
                            item.control.Show()
                            item.label.Show()
                        if item._aguidata.get('growable',False):
                            sizer.AddGrowableRow(row)                            
                        # USED TO BE FOR SASH ADJUST
                        # if item.label.preferredWidth > self.labelWidth:
                        #    self.labelWidth = item.label.preferredWidth
                        row+=1
                self.pugSizer.AddGrowableCol(1)                        
                sizer.Layout()
                # hack to make scrollbars resize
                size = self.GetSize()
                self.SetSize((20,20))
                self.SetSize(size)
                # end hack
        self.Thaw()
        wx.EndBusyCursor()

    def resize_puglist(self):
        """Recalculate the size of the puglist.
        
Generally, this is called when an attribute gui has changed size.
"""
        self.FitInside()

    def _init_viewMenu_Items(self, menu):
        #clear out menu items
        #wx has a bug with totally emptying radio items, so use satan as fake
        menu.AppendRadioItem(id=666, text='satan')
        for item in menu.MenuItems:
            if item.Id != 666:
                menu.DestroyItem(item)
        self._defaultView = 'Raw'
        self._currentView = None
        if (self.object):
            templateInfo = {}
            # look for templates specific to object's class
            if hasattr(self.object,'__class__'):
                templateInfo = get_template_info( self.object.__class__)
            # if necessary, look for templates assigned to object
            if not templateInfo and hasattr(self.object, '_pugTemplateClass'):
                templateInfo = get_template_info(self.object._pugTemplateClass)
            # as a last resort, use the default template
            if not templateInfo:
                templateInfo = get_template_info('default_template_info')
            if templateInfo.has_key('default'):
                defaultViewName = templateInfo['default']
            if templateInfo.has_key('templates'):
                # go through templateInfo and get names so we can sort them
                templateList = []
                rawList = []
                for name, template in templateInfo['templates'].iteritems():
                    if isinstance(template,dict):
                        templateList += [name]
                    else:
                        rawList += [name]
                templateList.sort()
                rawList.sort()
                templateList+=rawList
                # create _viewDict and menu items
                for name in templateList:
                    Id = wx.NewId()
                    template = templateInfo['templates'][name]
                    self._viewDict[Id] = template
                    self.Bind(wx.EVT_MENU, self._evt_viewmenu, id=Id)                    
                    menuItem = menu.Append(id=Id, 
                                     help=' '.join(['Show',name,'view']),
                                     text=name, kind=wx.ITEM_CHECK)
                    if name == defaultViewName:
                        self._defaultView = templateInfo['templates'][name]
                        menuItem.Check(True)
        menu.DestroyId(666)

    def _evt_viewmenu(self, event):
        for Id in self._viewDict:
            if Id == event.Id:
                self.viewMenu.Check(Id, True)
            else:
                self.viewMenu.Check(Id, False)
        self._currentView = self._viewDict[event.Id]
        self.create_puglist()        
        
    def apply_all(self, event = None):
        self._doingApply = True
        for item in self.pugList:
            item.apply()
        self._doingApply = False
        self.refresh_all()
        
    def _evt_kill_focus(self, event):
        pass
            
    def refresh_all(self, event = None):
        if self._doingApply:
            return
        for item in self.pugList:
            item.refresh()
        
    def get_label_window(self):
        return self
    
    def get_control_window(self):
        return self

    def show_help(self, event = None, object=None, attribute=""):
        if (object is None and attribute == "") or object == self:
            object = self.object
            objectPath = self.objectPath
            pugButton = False
        else:
            if self.objectPath:
                objectPath = ''.join([self.objectPath,".",attribute])
            else:
                objectPath = attribute
            pugButton = True
        if (self._helpFrame):
            self._helpFrame.Destroy()
        self._helpFrame = HelpFrame(object, self, attribute, objectPath, 
                                    pugButton)
        self._helpFrame.Center()
        self._helpFrame.Show()
        
    def _attach_setting(self, settingname, widget, id = None, default = None):
        """_attach_setting(self, setting, widget)

settingname: a string of the setting name (self.setting[settingname]) to attach
widget: the widget that contains the setting control 
id: id of menuItem or button. If not specified, defaults to widget id
default: starting value for the setting, if any
    
Currently accepeted widgets: toolbar togglebutton,  menu item
"""
        if id == None:
            id = widget.Id
        self._settingWidgets[id] = (widget, settingname)
        if default is not None:
            self.change_setting(settingname, default)
        else:
            self.settings[settingname] = None
        
    def _evt_setting(self, event):
        """_evt_setting(self, event)
        
Event handler for automatic setting system
"""
        id = event.Id
        widget, settingname = self._settingWidgets[id]
        self.change_setting(settingname, event.Selection, event)
        
    def change_setting(self, settingname, val, event = None):    
        """change_setting(self, setting, val)
        
Change a setting and the state of any widgets that control it
settingname: the setting string
val: the value to toggle it to. If None, just toggle it
Sets self.settings[settingname].
Automatically calls on_<setting>(val, event) callback.
    """
        if val is None:
            val = not self.settings[settingname]  
        for id, data in self._settingWidgets.iteritems():
            if settingname == data[1]:
                widget = data[0]
                if isinstance(widget, wx.Menu):
                    widget.Check(id,val)
                elif isinstance(widget, wx.ToolBar):
                    widget.ToggleTool(id, val)
        self.settings[settingname] = val
        # do callback
        callback = ''.join(["on_",settingname])
        if hasattr(self,callback):
            getattr(self,callback)(val, event)

    def on_hide_1_underscore(self, val, event = None):
        if val and not self.settings['hide_2_underscore']:
            self.change_setting('hide_2_underscore', 1, event)
        elif self.pugList:            
            self.create_puglist()

    def on_hide_2_underscore(self, val, event = None):
        if not val and self.settings['hide_1_underscore']:
            self.change_setting('hide_1_underscore', 0, event)
        elif self.pugList:            
            self.create_puglist()

    def on_auto_refresh(self, val, event = None):
        """if val, do a refresh and set timer to do the next one, else stop"""
        if val:
            self._auto_refresh(250)
        elif self._auto_refresh_timer:
            self._auto_refresh_timer.Stop()
            
    def _auto_refresh(self, msecs):
        self.refresh_all()
        self._auto_refresh_timer = wx.CallLater(msecs, self._auto_refresh, 100)
            
    def _evt_on_close(self, event=None):
        self.on_auto_refresh(False)
        event.Skip()
                    
    def _init_fileMenu_Items(self, menu):
        for item in menu.MenuItems:
            menu.DestroyItem(item)

        menu.Append(help='Save object state as...', id = _MENU_SAVE_AS, 
                      text = 'Save State As...\tShift+Ctrl+S')
        menu.Append(help='Save object state', id = _MENU_SAVE, 
                      text = 'Save State\tCtrl+S')
        menu.Append(help='Load a saved object state', id = _MENU_LOAD, 
                      text = 'Load State\tCtrl+L')
        self.Bind(wx.EVT_MENU, self.save_object_state_as, id = _MENU_SAVE_AS)
        self.Bind(wx.EVT_MENU, self.save_object_state, id = _MENU_SAVE)
        self.Bind(wx.EVT_MENU, self.load_object_state, id = _MENU_LOAD)
        # TODO: put in little save icons
        menu.AppendSeparator()
        menu.Append(help='Export object as python class code',
                      id = _MENU_EXPORT_CLASS, 
                      text='Export class code\tCtrl+E')
        menu.Append(help='Export object as python class code as ...',
                      id = _MENU_EXPORT_CLASS_AS, 
                      text='Export class code as ...\tShift+Ctrl+E')
        menu.AppendSeparator()
        menu.Append(help='Export object as python object code',
                      id = _MENU_EXPORT_OBJECT, 
                      text='Export object code\tCtrl+O')
        menu.Append(help='Export object as python object code as ...',
                      id = _MENU_EXPORT_OBJECT_AS, 
                      text='Export object code as ...\tShift+Ctrl+O')
        self.Bind(wx.EVT_MENU, self.code_export, id = _MENU_EXPORT_OBJECT)
        self.Bind(wx.EVT_MENU, self.code_export_as, id = _MENU_EXPORT_OBJECT_AS)
        self.Bind(wx.EVT_MENU, self.code_export, id = _MENU_EXPORT_CLASS)
        self.Bind(wx.EVT_MENU, self.code_export_as, id = _MENU_EXPORT_CLASS_AS)
    
    def code_export(self, event = None):
        if self.hasSavedAs.get(event.Id + 1):
            lastfolder, lastfilename = self.hasSavedAs.get(event.Id + 1)
            self.apply_all()
            if event.Id in [ _MENU_EXPORT_CLASS, _MENU_EXPORT_CLASS_AS]:
                asClass = True
            else:
                asClass = False
            try:
                code_export(self.object, 
                            os.path.join(lastfolder, lastfilename), 
                            asClass)
            except:
                retDlg = wx.MessageDialog(self, ':'.join([str(exc_info()[0]),
                                                          str(exc_info()[1])]),
                                          'Unable To Export', 
                                           wx.ICON_ERROR | wx.OK)
                retDlg.ShowModal()                
        else:
            event.Id += 1
            self.code_export_as(event)
                    
    def code_export_as(self, event = None):
        if self.hasSavedAs.get(event.Id):
            defaultfolder, defaultfilename = self.hasSavedAs.get(event.Id)
        else:
            defaultfolder = self.defaultFolder
            if event.Id in [ _MENU_EXPORT_CLASS, _MENU_EXPORT_CLASS_AS]:
                defaultfilename = ''.join([self.defaultFilename,'.py'])
            else:
                defaultfilename = ''.join([self.defaultFilename,'_obj.py'])
        if event.Id in [ _MENU_EXPORT_CLASS, _MENU_EXPORT_CLASS_AS]:
            title = "Export object as python class code..."
        else:
            title = "Export object as python object code..."
        dlg = wx.FileDialog(self, title, 
                            defaultfolder, defaultfilename,
                            "Pug Python file (*.py)|*.py",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:        
            self.hasSavedAs[event.Id] = (dlg.GetDirectory(),dlg.GetFilename())
            event.Id -= 1
            self.code_export(event)
        dlg.Destroy()

    def _init_PrivateDataMenu_Items(self, parent):
        parent.Append(help='Hide "_" and "__" attributes in raw views',
                   id=_MENU_HIDE1UNDERSCORE, kind=wx.ITEM_CHECK, 
                   text=u'Hide "_" attributes\tCtrl+1')
        parent.Append(help='Hide "__" attributes in raw views', 
                   id=_MENU_HIDE2UNDERSCORE, kind=wx.ITEM_CHECK, 
                   text=u'Hide "__" attributes\tCtrl+2')
        self.Bind(wx.EVT_MENU, self._evt_setting,
              id=_MENU_HIDE1UNDERSCORE)
        self.Bind(wx.EVT_MENU, self._evt_setting,
              id=_MENU_HIDE2UNDERSCORE)
        self._attach_setting("hide_1_underscore", parent, _MENU_HIDE1UNDERSCORE)
        self._attach_setting("hide_2_underscore", parent, _MENU_HIDE2UNDERSCORE)
        self.change_setting("hide_1_underscore", 1)

    def save_object_state(self, event = None):
        if self.hasSavedAs.get(event.Id + 1):
            lastfolder, lastfilename = self.hasSavedAs.get(event.Id + 1)
            self.apply_all()
            try:
                pugSave(self.object, os.path.join(lastfolder, lastfilename))
            except:
                retDlg = wx.MessageDialog(self, str(exc_info()[0]),
                                          'Unable To Save State', wx.OK)
                retDlg.ShowModal()                            
        else:
            event.Id += 1
            self.save_object_state_as( event)
        
    def save_object_state_as(self, event = None):
        if self.hasSavedAs.get(event.Id):
            defaultfolder, defaultfilename = self.hasSavedAs.get(event.Id)
        else:
            defaultfolder = self.defaultFolder
            defaultfilename = ''.join([self.defaultFilename,'.pug'])        
        dlg = wx.FileDialog(self, "Save State as...", 
                            defaultfolder, defaultfilename,
                            "Pug Object State (*.pug)|*.pug",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:        
            self.hasSavedAs[event.Id] = (dlg.GetDirectory(), dlg.GetFilename())
            event.Id -= 1
            self.save_object_state(event)
        dlg.Destroy()
        
    def load_object_state(self, event = None):
        app = wx.GetApp()
        filename = ''.join([self.defaultFilename,'.pug'])            
        dlg = wx.FileDialog(self, "Load State", 
                            self.defaultFolder, filename,
                            "Pug Object State (*.pug)|*.pug", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:        
            filepath = dlg.GetPath()
            pugLoad(self.object, filepath)
            self.refresh_all()
            fname,ext = os.path.splitext(dlg.GetFilename())
            self.defaultFilename = fname
            self.defaultFolder = dlg.GetDirectory()
            self.hasSaved = True
        dlg.Destroy()        

    def make_toolbar(self):
        self.toolBar = wx.ToolBar(parent=self.GetParent(),
              pos=wx.Point(0, 64), size=wx.Size(25, 34),
              style=wx.RAISED_BORDER | wx.TB_HORIZONTAL)
        self.toolBar.SetAutoLayout(True)
        self.toolBar.Hide()
        #self.toolBar.SetBackgroundColour(wx.Colour(222, 222, 222))
        #self.SetToolBar(self.toolBar)
        buttonsize = WX_BUTTON_BMP_SIZE
        self.toolBar.SetToolBitmapSize(buttonsize)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, 
                                           wx.ART_TOOLBAR, buttonsize)
        self.toolBar.AddCheckLabelTool(_TOOL_AUTOREFRESH, "Refresh", bitmap=bmp, 
                            shortHelp ="Auto Refresh", 
                            longHelp ="Refresh values every 0.25 seconds")
        refreshButton = wx.Button(self.toolBar, _TOOL_REFRESH, "Refresh")
        self.toolBar.AddControl(refreshButton)
        self.toolBar.AddSeparator()
        refreshButton.Bind(wx.EVT_BUTTON, self.refresh_all) 
        self.toolBar.Bind(wx.EVT_TOOL, self._evt_setting, 
                       id=_TOOL_AUTOREFRESH)      
        self._attach_setting("auto_refresh", self.toolBar, _TOOL_AUTOREFRESH, 
                     False)
        
        bmp = wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, 
                                           wx.ART_TOOLBAR, buttonsize)
        self.toolBar.AddCheckLabelTool(_TOOL_AUTOAPPLY, "Auto", bitmap=bmp, 
                    shortHelp="Auto Apply", 
                    longHelp="Apply all changes to object automatically")
        applyButton = wx.Button(self.toolBar, _TOOL_APPLY, "Apply")
        self.toolBar.AddControl(applyButton)
        self.toolBar.AddSeparator()
        applyButton.Bind(wx.EVT_BUTTON, self.apply_all)            
        self.toolBar.Bind(wx.EVT_TOOL, self._evt_setting, 
                       id=_TOOL_AUTOAPPLY)       
        self._attach_setting("auto_apply", self.toolBar, _TOOL_AUTOAPPLY, 
                     True)        
        
        helpID = wx.NewId()
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, 
                                           wx.ART_TOOLBAR, buttonsize)
        self.toolBar.AddSimpleTool(helpID, bmp, "View help", 
                                "View help info for this object")
        context = wx.ContextHelpButton(self.toolBar)
        context.SetToolTipString(
                             "Click here, then click on any attribute label")
        self.toolBar.AddControl(context)
        self.toolBar.Bind(wx.EVT_TOOL, self.show_help, id=helpID)
        self.toolBar.Realize()
        
#    USED TO BE FOR ADJUSTABLE LABEL/CONTROL SPLIT POINT
#    def _evt_splitter_dclick( self, event=None):
#        self.splitterWindow.SetSashPosition( self.labelWidth)        
                    
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        self._init_utils()
        #self.SetMinSize(wx.Size(150, 130))
        
        self.make_toolbar()
                
    def show_all_attributes(self, event = None):
        """Expand the frame's size so that all attributes are visible"""
        self._evt_splitter_dclick( self)     
           
        maximizeSize = self.splitterWindow.GetSize()
        # fudge it for now... not sure how to get exactly the right size
        maximizeSize[0] += 20
        maximizeSize[1] += 20
        self.GetParent().SetClientSize(maximizeSize)

    def _init_optionsMenu_Items(self, parent):
        # generated method, don't edit
        parent.AppendMenu(help='Show/Hide private attributes', 
                          id = wx.NewId(),
                          submenu=self.privateDataMenu, 
                          text=u'Private Data')
        
    def _init_menuBar_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.fileMenu, title=u'Export')
        parent.Append(menu=self.viewMenu, title=u'View')
        parent.Append(menu=self.optionsMenu, title=u'Options')

    def _init_utils(self):
        # generated method, don't edit
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.viewMenu = wx.Menu()
        self.optionsMenu = wx.Menu()
        self.privateDataMenu = wx.Menu()

        self._init_menuBar_Menus(self.menuBar)
        self._init_optionsMenu_Items(self.optionsMenu)
        self._init_PrivateDataMenu_Items(self.privateDataMenu)

_TOOL_AUTOAPPLY = wx.NewId()
_TOOL_APPLY = wx.NewId()
_TOOL_AUTOREFRESH = wx.NewId()
_TOOL_REFRESH = wx.NewId()
_MENU_HIDE1UNDERSCORE = wx.NewId()
_MENU_HIDE2UNDERSCORE = wx.NewId()
_MENU_SAVE = wx.NewId()
_MENU_SAVE_AS = wx.NewId()
_MENU_LOAD = wx.NewId()
_MENU_EXPORT_CLASS = wx.NewId()
_MENU_EXPORT_CLASS_AS = wx.NewId()
_MENU_EXPORT_OBJECT = wx.NewId()
_MENU_EXPORT_OBJECT_AS = wx.NewId()

#settingDict contains correspondences between controls and setting fields
_settingDict = {_TOOL_AUTOAPPLY:"auto_apply", 
            _TOOL_AUTOREFRESH:"auto_refresh",
            _MENU_HIDE1UNDERSCORE:"hide_1_underscore",
            _MENU_HIDE2UNDERSCORE:"hide_2_underscore"
            }