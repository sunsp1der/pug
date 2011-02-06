"""The basic pug display window.

A scrolled panel that holds all the pug aguis. Also creates menus and a toolbar,
though you need a frame for those...
"""
#some code looks a little mumbo-jumboey because it was made by BOA

# TODO: provide interface for creating attribute
# TODO: menu option to go to file where this is defined
# TODO: send aguilist a specific list of attributes
# TODO: allow personalized toolbars

import re
import os.path
import inspect
from weakref import ref, proxy, ProxyTypes
from sys import exc_info

import wx
import wx.lib.scrolledpanel
import wx.lib.buttons

from pug.aguilist import create_raw_aguilist, create_pugview_aguilist
from pug.util import get_simple_name, get_code_file, start_edit_process
from pug.storage import pugSave, pugLoad
from pug.constants import *
from pug.syswx.helpframe import HelpFrame
from pug.syswx.wxconstants import *
from pug.syswx.util import show_exception_dialog, cache_aguilist
from pug.pugview_manager import get_obj_pugview_info
from pug.code_storage import code_exporter

#_DEBUG
_DEBUG = False

class PugWindow(wx.lib.scrolledpanel.ScrolledPanel):
    """A scrolled window that holds a Python Universal GUI
    
PugWindow( parent, obj=None, objectpath="object", title="", show=True)
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
    titleBase = ''
    aguilist = []
    _viewDict = {}
    _currentView = {}
    msgTextCtrl = None
    pugview = {}
    _helpFrame =  None # currently open help frame
    _autoRefreshTimer = None # timer object that refreshes frame
    _doingApply = False # currently in the middle of an apply all
    _currentView = {}
    def __init__(self, parent, obj=None, objectpath="unknown", title=""):        
        #windows
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, 
                        pos=wx.Point(0, 0), size=WX_PUGFRAME_DEFAULT_SIZE,
                        style=wx.SUNKEN_BORDER)
        #attributes
        self.hasSavedAs = {} # save/export event.Id: (folder, filename)
        self.aguilist = [] # list of pug attribute guis describing object
        self.settings = {'hide_1_underscore':True, 'hide_2_underscore':True,
                         'auto_apply':True, 'auto_refresh':False}
        self._settingWidgets = {} # internal list of setting control widgets
        self._viewDict = {}
        self.objectPath = objectpath
        self.defaultFolder = wx.GetApp().projectFolder
        self.MinSize = (-1,-1)
        self.SetScrollRate(1,5)
        self.pugSizer = wx.GridBagSizer()
        self.SetSizer(self.pugSizer)
        self._init_ctrls() #BOA GENERATED STUFF
        
        #set up actual object gui
        self.set_object(obj, objectpath, title)     
        
    def __del__(self):
        cache_aguilist( self.aguilist)
      
    def GetBestSize(self):
        size = self.pugSizer.CalcMin()
        if self.pugSizer.GetColWidths():
            # double the label width
            niceWidth = self.pugSizer.GetColWidths()[0]*2 
            if size[0] < niceWidth:
                size = (niceWidth,size[1])
        return size
        
    def set_object(self, obj, objectpath="unknown", title=None):
        if _DEBUG: print "pugwindow.set_object", obj
        self.Freeze()
        wx.BeginBusyCursor()
        self.shortPath = get_simple_name(obj, objectpath)
        self.defaultFilename = self.shortPath
        if objectpath == "unknown":
            self.objectPath = self.shortPath
        else:
            self.objectPath = objectpath
        if not title:
            if obj:                
                #set up title
                title = self.shortPath
                if self.shortPath != self.objectPath:                
                    if self.objectPath:
                        title = ''.join([title, ' (',self.objectPath,')'])
            else:
                title = "Pug Window: No object"

        if self.objectRef and obj and obj is self.objectRef():
            self.display_aguilist()
        else:        
            self.stopped_viewing()
            oldobject = self.object
            if not obj:
                self.objectRef = None
                self.object = obj
#                self.display_message("No object")
                self.setup_menus()
            else:
                try:
                    self.objectRef = ref(obj)
                    self.object = proxy(obj, self._schedule_object_deleted)
                except:
                    def objectRef():
                        return obj
                    self.objectRef = objectRef
                    self.object = obj # this will prevent obj from being deleted
                oldView = self._currentView
                self._currentView = {}
                self.setup_menus()
                if oldView == self._currentView:
                    self.update_aguilist_object()
                else:
                    self.create_aguilist()
                try:
                    if not oldobject and hasattr(self.GetParent(), 
                                                 'show_all_attributes'):
                        self.GetParent().show_all_attributes()
                except:
                    pass
            self.started_viewing( obj)
        self.SetTitle(title)
        if self.IsFrozen():
            self.Thaw()                   
        wx.EndBusyCursor()        
    
    def stopped_viewing(self):
        """stopped_viewing()
        
tell app that our parent isn't viewing the current object"""
        if self.objectRef:
            wx.GetApp().frame_stopped_viewing(self.GetParent(), 
                                                 self.objectRef)

    def started_viewing(self, objectRef):
        """started-viewing(obj)
tell app that our parent is viewing obj"""
        wx.GetApp().frame_started_viewing(self.GetParent(), objectRef)             
        
    
    def SetTitle(self, title):
        self.titleBase = title
        parent = self.GetParent()
        if hasattr(parent, 'SetTitle'):
            parent.SetTitle(title)        

    def _schedule_object_deleted(self=None, obj=None):
        if not wx.GetApp():
            return
        wx.CallAfter(self._object_deleted, obj)
        
    def _object_deleted(self, obj=None):
        if not self.msgTextCtrl:
            title = ''.join([ self.titleBase," (deleted)"])
            self.set_object(None, title=title)
            self.display_message(title)

    def display_message(self, message):
        """display_message( message)
        
Set the PugWindow to display a simple text message rather than view an object.
To return to object view, call display_aguilist().
"""
        if self.msgTextCtrl:
            self.msgTextCtrl.SetLabel(message)
        else:
            sizer = self.pugSizer
            sizer.ShowItems( False)
            sizer.Clear(False)
            self.reset_sizer()
            text = wx.StaticText( self, label = message)
            self.msgTextCtrl = text
            sizer.Add(self.msgTextCtrl, (0,0), flag = wx.ALIGN_CENTER)
            sizer.AddGrowableRow(0)
            sizer.AddGrowableCol(0)       
            sizer.Layout()
        
    def reset_sizer(self):
        sizer = self.pugSizer
        rows = range(sizer.GetRows())
        for row in rows:
            try:
                sizer.RemoveGrowableRow(row)
            except:
                pass
        cols = range(sizer.GetCols())
        for col in cols:
            try:
                sizer.RemoveGrowableCol(col)
            except:
                pass
        sizer.SetRows(0)
        sizer.SetCols(0)
        self.SetupScrolling()

    def create_aguilist(self):
        wx.BeginBusyCursor()
        self.Freeze()
        cache_aguilist(self.aguilist)
        filterUnderscore = 0
        if self.settings['hide_1_underscore']:
            filterUnderscore = 1
        elif self.settings['hide_2_underscore']:
            filterUnderscore = 2
        oldpugview = self.pugview
        self.pugview = {}
        if self._currentView in ('&Raw', 'Raw'):
            self.aguilist = create_raw_aguilist(self.object, self, None, 
                                              filterUnderscore)
        elif self._currentView in ('Raw &Data', 'Raw Data'):
            self.aguilist = create_raw_aguilist(self.object, self, 
                                              ['Default', 'Objects'],
                                              filterUnderscore)
        elif self._currentView in ('Raw &Methods', 'Raw Methods'):
            self.aguilist = create_raw_aguilist(self.object, self,['Routine'],
                                              filterUnderscore)
        else:
            pugview = self._currentView
            self.pugview = pugview
            self.aguilist = create_pugview_aguilist(self.object, self, pugview,
                                                    filterUnderscore=0)
            self.SetSize(wx.Size(pugview['size'][0], 
                                 pugview['size'][1]))
            if pugview.get('force_persist'):
                self.persist = self.objectRef()
            else:
                self.persist = None
        self.display_aguilist()
        if self.IsFrozen():
            self.Thaw()
        wx.EndBusyCursor()
        
    def update_aguilist_object(self):
        for agui in self.aguilist:
            agui.setup( agui.attribute, agui.window, agui.aguidata)
        if self.msgTextCtrl:
            self.display_aguilist()
        else:
            self.refresh()

    def display_aguilist(self):
        wx.BeginBusyCursor()    
        self.Freeze()
        if _DEBUG: print "PugWindow.display_aguilist enter"
        if self.msgTextCtrl:
            self.msgTextCtrl.Destroy()
            self.msgTextCtrl = None
        if self.object:
            if self.aguilist:         
                sizer = self.pugSizer
                #clear aguilist
                sizer.Clear(False)
                self.reset_sizer()
                #set up attributeguis
                # self.labelWidth = 0 # USED TO BE FOR SASH ADJUST
                row = 0
                for item in self.aguilist:
                    if _DEBUG: print "   PugWindow.display_aguilist item:", \
                                    item.attribute, item
                    try:
                        item.refresh()
                    except:
                        item.label.Hide()
                        item.control.Hide()
                        pass
                    else:
                        if item.aguidata.get('control_only', False):
                            # span across label and control
                            sizer.Add(item.control, (row,0), (1,2),
                                      flag=wx.EXPAND | wx.SOUTH, 
                                      border=WX_PUGLIST_YSPACER)
                            if item.label:
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
                        if item.aguidata.get('growable',False):
                            sizer.AddGrowableRow(row)                            
                        # USED TO BE FOR SASH ADJUST
                        # if item.label.preferredWidth > self.labelWidth:
                        #    self.labelWidth = item.label.preferredWidth
                        row+=1
                self.pugSizer.AddGrowableCol(1)                        
                # hack to make scrollbars resize
                # sizer.Layout()
                # self.GetParent().GetSizer().Layout()
                # size = self.GetSize()
                # self.SetSize((20,20))
                # self.SetSize(size)
                # end hack
                parent = self.GetParent()
                size = parent.GetSize()
                parent.SetSize((1,1))
                parent.SetSize(size)  
                parent.Layout()              
        if _DEBUG: print "PugWindow.display_aguilist exit"
        if self.IsFrozen():
            self.Thaw()
        wx.EndBusyCursor()

    def resize_aguilist(self):
        """Recalculate the size of the aguilist.
        
Generally, this is called when an attribute gui has changed size.
"""
        self.FitInside()
        
    def OnChildFocus(self, event):
        if isinstance(event.EventObject, wx.lib.buttons.GenButton):
            pass
        else:
            event.Skip()
            
    def setup_menus(self):
        if not hasattr(self, 'menuBar'):
            self.menuBar = wx.MenuBar()
        self.menuBar.Freeze()
        self.menuBar.SetMenus([])
        wx.GetApp().append_global_menus(self.menuBar)
        if self.object:
            self._init_viewMenu_Items(self.viewMenu)
            self.menuBar.Append(self.viewMenu,'&View')
            self.menuBar.Append(self.exportMenu,'&Export')
            self.menuBar.Append(self.helpMenu,'&Help')
            if isinstance(self._currentView, dict):
                skipMenus = self._currentView.get('skip_menus',[])
            else:
                skipMenus = []
            for menu in skipMenus:
                # to remove globals or others
                skipper = self.menuBar.FindMenu(menu)
                if skipper:
                    self.menuBar.Remove(skipper)
        self.menuBar.Thaw()
#        else:
#            pass #self._init_viewMenu_Items(self.viewMenu)
            
    def _init_viewMenu_Items(self, menu):
        #clear out menu items
        #wx has a bug with totally emptying radio items, so use a dummy
        menu.AppendRadioItem(id=1, text='dummy')
        idDict = {}
        for item in menu.MenuItems:
            pugview = self._viewDict.get(item.Id, None)
            if pugview:
                idDict[id(pugview)] = item.Id
            menu.DestroyItem(item)
        if (self.object):
            pugviewInfo = get_obj_pugview_info(self.object)
            defaultViewName = pugviewInfo.get('default','Raw')
            if pugviewInfo.has_key('pugviews'):
                # go through pugviewInfo and get names so we can sort them
                pugviewList = []
                rawList = []
                for name, pugview in pugviewInfo['pugviews'].iteritems():
                    if isinstance(pugview,dict):
                        pugviewList += [name]
                    else:
                        rawList += [name]
                pugviewList.sort()
                rawList.sort()
                pugviewList += rawList
                pugviewList.reverse()
                # create _viewDict and menu items
                for name in pugviewList:
                    pugview = pugviewInfo['pugviews'][name]
                    Id = idDict.get(id(pugview), wx.NewId())
                    self._viewDict[Id] = pugview
                    self.Bind(wx.EVT_MENU, self._evt_viewmenu, id=Id)                    
                    menuItem = menu.Prepend(id=Id, 
                                     help=' '.join(['Show',name,'view']),
                                     text=name, kind=wx.ITEM_CHECK)
                    if not self._currentView and name == defaultViewName:
                        self._currentView = pugviewInfo['pugviews'][name]
                    if pugview == self._currentView:
                        menuItem.Check(True)
                    else:
                        menuItem.Check(False)
            if type(self._currentView) == str:
                #private data options for Raw menus
                menu.AppendSeparator()
                self._add_PrivateDataMenu_Items(menu) 
            menu.AppendSeparator()
            self._add_StandardView_Items(menu)
            self.refresh_settings()
#        menu.DestroyId(1)

    def _evt_viewmenu(self, event):
        if self._currentView != self._viewDict[event.Id]:
            self._currentView = self._viewDict[event.Id]
            self.setup_menus()
            self.create_aguilist()      
        for Id in self._viewDict:
            if Id == event.Id:
                self.viewMenu.Check(Id, True)
            else:
                self.viewMenu.Check(Id, False)
        
    def apply(self, event=None):
        if not self.settings['auto_apply'] and event.Id != _TOOL_APPLY:
            return
        if not self.objectRef or not self.objectRef():
            return
        self._doingApply = True
        if _DEBUG: print "pugwindow.apply", self.object
        for item in self.aguilist:
            if _DEBUG: print item.attribute
            item.apply()
        self._doingApply = False
        self.refresh()
        if _DEBUG: print "DONE apply\n"

    def refresh(self, event=None):
        if self._doingApply:
            return
        if not self.objectRef or not self.objectRef():
            return
        if _DEBUG: print "pugwindow.refresh", self.object
        for item in self.aguilist:
            if _DEBUG: print item.attribute
            item.refresh()
        if _DEBUG: print "DONE refresh\n"

    def help_context(self, event=None):
        help = wx.ContextHelp( self, False)
        help.BeginContextHelp() 
        help.EndContextHelp()
    
    def show_help(self, event=None, object=None, attribute=""):
        customFrame = None
        try:
            if event and event.Id == _HELP_INFO:
                # this indicates that the 'info' button was pushed
                object = self.objectRef()
                objectPath = self.objectPath
                pugButton = True
                retypeButton = False
                custom_info = None
                try: 
                    custom_info = self.pugview.get_key('info_function')
                except:
                    pass
                if custom_info:
                    customFrame = custom_info(object, self, objectPath)
            elif (object is None and attribute == ""):    
                # context help pushed, but no valid context            
                return
            else:
                # context help
                if self.objectPath:
                    objectPath = ''.join([self.objectPath,".",attribute])
                else:
                    objectPath = attribute
                pugButton = True
                retypeButton = True
            if (self._helpFrame):
                self._helpFrame.Destroy()
            if customFrame:
                self._helpFrame = customFrame
            else:
                self._helpFrame = HelpFrame(object, self, attribute, objectPath, 
                                            pugButton, retypeButton)
            self._helpFrame.Center()
            self._helpFrame.Show()
        except:
            retDlg = wx.MessageDialog(self, 'Unable To Open Help',
                                      'Error', 
                                       wx.ICON_ERROR | wx.OK)
            retDlg.ShowModal()    
            retDlg.Destroy()                      
        
    def _attach_setting(self, settingname, widget, id=None, default='!@#$$^&*'):
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
        if default != '!@#$$^&*': # assuming that will never be the real default
            self.change_setting(settingname, default)
        
    def _evt_setting(self, event):
        """_evt_setting(self, event)
        
Event handler for automatic setting system
"""
        id = event.Id
        widget, settingname = self._settingWidgets[id]
        self.change_setting(settingname, event.Selection, event)
        
    def change_setting(self, settingname, val, event=None):    
        """change_setting(self, setting, val)
        
Change a setting and the state of any widgets that control it
settingname: the setting string
val: the value to toggle it to. If None, just toggle it
Sets self.settings[settingname].
Automatically calls on_<setting>(val, event) callback.
    """
        oldsetting = self.settings.get(settingname,not val)
        if val is None:
            val = not oldsetting
        for id, data in self._settingWidgets.iteritems():
            if settingname == data[1]:
                widget = data[0]
                if widget and isinstance(widget, wx.Menu) and \
                                                widget.FindItemById(id):
                    widget.Check(id,val)
                elif widget and isinstance(widget, wx.ToolBar):
                    widget.ToggleTool(id, val)
        self.settings[settingname] = val
        # do callback
        if val != oldsetting:
            callback = ''.join(["on_",settingname])
            if hasattr(self,callback):
                getattr(self,callback)(val, event)                
                
    def view_source_code(self, event=None):
        if hasattr(self.object, '_get_source_code'):
            file = self.object._get_source_code()
        else:
            file = get_code_file(self.object)
        if file:
            wx.GetApp().code_editor.open_code_file( file)

    def open_shell(self, event=None):
        """This opens a pug_shell for the window's object"""
        info = {'rootObject':self.object, 
                'rootLabel':self.shortPath,
                 'locals':{self.shortPath:self.object}}
        if hasattr(self.object, '_get_shell_info'):
            new_info = self.object._get_shell_info()
            info.update(new_info)        
        wx.GetApp().code_editor.open_shell(**info)
            
    def refresh_settings(self):
        for setting in self.settings:
            self.change_setting(setting, self.settings[setting])

    def on_hide_1_underscore(self, val, event=None):
        if val and not self.settings['hide_2_underscore']:
            self.change_setting('hide_2_underscore', 1, event)
        elif self.aguilist:            
            self.create_aguilist()

    def on_hide_2_underscore(self, val, event=None):
        if not val and self.settings['hide_1_underscore']:
            self.change_setting('hide_1_underscore', 0, event)
        elif self.aguilist:            
            self.create_aguilist()

    def on_auto_refresh(self, val, event=None):
        """if val, do a refresh and set timer to do the next one, else stop"""
        if val:
            self._auto_refresh(250)
        elif self._autoRefreshTimer:
            self._autoRefreshTimer.Stop()
            
    def _auto_refresh(self, msecs):
        try:
            self.refresh()
        except:
            print "_auto_refresh error:\n",exc_info()
            show_exception_dialog()
        else:   
            self._autoRefreshTimer = wx.CallLater(msecs, 
                                                  self._auto_refresh, msecs)
                    
    def _init_helpMenu_Items(self, menu):
        menu.Append(help='View information about this object', id=_HELP_INFO, 
                    text='Object &Info')
        menu.Append(help='Get context help on object attributes', 
                    id=_HELP_CONTEXT, text='&Context Info')
                    
    def _init_fileMenu_Items(self, menu):
        menu.Append(help='Save object state as...', id = _MENU_SAVE_AS, 
                      text = 'Save State &As...')
        menu.Append(help='Save object state', id = _MENU_SAVE, 
                      text = '&Save State')
        menu.Append(help='Load a saved object state', id = _MENU_LOAD, 
                      text = '&Load State')
        menu.AppendSeparator()
        menu.Append(help='Export object as python class code',
                      id = _MENU_EXPORT_CLASS, 
                      text='Export &class code')
        menu.Append(help='Export object as python class code as ...',
                      id = _MENU_EXPORT_CLASS_AS, 
                      text='E&xport class code as ...')
        menu.AppendSeparator()
        menu.Append(help='Export object as python object code',
                      id = _MENU_EXPORT_OBJECT, 
                      text='Export &object code')
        menu.Append(help='Export object as python object code as ...',
                      id = _MENU_EXPORT_OBJECT_AS, 
                      text='Export o&bject code as ...')
   
    def code_export(self, event=None):
        if self.hasSavedAs.get(event.Id + 1):
            lastfolder, lastfilename = self.hasSavedAs.get(event.Id + 1)
            self.apply()
            if event.Id in [ _MENU_EXPORT_CLASS, _MENU_EXPORT_CLASS_AS]:
                asClass = True
            else:
                asClass = False
            try:
                code_exporter(self.object, 
                            os.path.join(lastfolder, lastfilename), 
                            asClass)
            except:
                show_exception_dialog(self)
        else:
            event.Id += 1
            self.code_export_as(event)
                    
    def code_export_as(self, event=None):
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
        
    def _add_PrivateDataMenu_Items(self, parent):
        parent.Append(help='Hide "_" and "__" attributes in raw views',
                   id=_MENU_HIDE1UNDERSCORE, kind=wx.ITEM_CHECK, 
                   text=u'&Hide "_" attributes')
        parent.Append(help='Hide "__" attributes in raw views', 
                   id=_MENU_HIDE2UNDERSCORE, kind=wx.ITEM_CHECK, 
                   text=u'H&ide "__" attributes')
        has_settings = self.settings.has_key('hide_1_underscore')
        self._attach_setting("hide_1_underscore", parent, 
                             _MENU_HIDE1UNDERSCORE)
        self._attach_setting("hide_2_underscore", parent, 
                             _MENU_HIDE2UNDERSCORE)
        if not has_settings:
            self.change_setting("hide_1_underscore", 1)

            
    def _add_StandardView_Items(self, parent):
        parent.Append(help='Apply values to object',
                      id=_TOOL_APPLY, text=u'&Apply\tF6')
        parent.Append(help='Refresh values', 
                   id=_TOOL_REFRESH, text=u'&Refresh\tF5')
        parent.Append(id=_TOOL_AUTOAPPLY, kind=wx.ITEM_CHECK, 
            help='When off, only apply changes when Apply is selected',
            text=u'A&uto-Apply')
        parent.Append(help='Refresh values every 0.25 seconds', 
                   id=_TOOL_AUTOREFRESH, kind=wx.ITEM_CHECK, 
                   text=u'Au&to-Refresh')        
        self._attach_setting("auto_apply", parent, _TOOL_AUTOAPPLY, True)        
        self._attach_setting("auto_refresh", parent, _TOOL_AUTOREFRESH, False)
        skip_source = type(self._currentView) is dict and \
                            self._currentView.get('no_source', False)
        skip_shell = type(self._currentView) is dict and \
                            self._currentView.get('no_shell', False)
        if not skip_source or not skip_shell:
            parent.AppendSeparator()
        if not skip_source:  
            parent.Append(help="View object's source file", 
                   id=_TOOL_VIEWSOURCE, text=u'View source &code\tCtrl+U')
        if not skip_shell:
            parent.Append(help="Open a python shell for this object",
                      id=_TOOL_SHELL, text=u'Open &shell\tCtrl+P')      

    def save_object_state(self, event=None):
        if self.hasSavedAs.get(event.Id + 1):
            lastfolder, lastfilename = self.hasSavedAs.get(event.Id + 1)
            self.apply()
            try:
                pugSave(self.object, os.path.join(lastfolder, lastfilename))
            except:
                retDlg = wx.MessageDialog(self, str(exc_info()[0]),
                                          'Unable To Save State', wx.OK)
                retDlg.ShowModal()     
                retDlg.Destroy()                                       
        else:
            event.Id += 1
            self.save_object_state_as( event)
        
    def save_object_state_as(self, event=None):
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
        
    def load_object_state(self, event=None):
        app = wx.GetApp()
        filename = ''.join([self.defaultFilename,'.pug'])            
        dlg = wx.FileDialog(self, "Load State", 
                            self.defaultFolder, filename,
                            "Pug Object State (*.pug)|*.pug", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:        
            filepath = dlg.GetPath()
            pugLoad(self.object, filepath)
            self.refresh()
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
        refreshButton.Bind(wx.EVT_BUTTON, self.refresh) 
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
        applyButton.Bind(wx.EVT_BUTTON, self.apply)            
        self.toolBar.Bind(wx.EVT_TOOL, self._evt_setting, 
                       id=_TOOL_AUTOAPPLY)       
        self._attach_setting("auto_apply", self.toolBar, _TOOL_AUTOAPPLY, 
                     True)        
        
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, 
                                           wx.ART_TOOLBAR, buttonsize)
        self.toolBar.AddSimpleTool(_HELP_INFO, bmp, "View help", 
                                "View help info for this object")
        context = wx.ContextHelpButton(self.toolBar)
        context.SetToolTipString(
                             "Click here, then click on any attribute label")
        self.toolBar.AddControl(context)
        self.toolBar.Bind(wx.EVT_TOOL, self.show_help, id=_HELP_INFO)
        self.toolBar.Realize()
        
    def _init_ctrls(self):
        self.menuBar = wx.MenuBar()
        self.exportMenu = wx.Menu()
        self.viewMenu = wx.Menu()
        self.helpMenu = wx.Menu()
        self._init_fileMenu_Items(self.exportMenu)
        self._init_helpMenu_Items(self.helpMenu)
        #export menu
        self.Bind(wx.EVT_MENU, self.save_object_state_as, id = _MENU_SAVE_AS)
        self.Bind(wx.EVT_MENU, self.save_object_state, id = _MENU_SAVE)
        self.Bind(wx.EVT_MENU, self.load_object_state, id = _MENU_LOAD)
        self.Bind(wx.EVT_MENU, self.code_export, id = _MENU_EXPORT_OBJECT)
        self.Bind(wx.EVT_MENU, self.code_export_as, id = _MENU_EXPORT_OBJECT_AS)
        self.Bind(wx.EVT_MENU, self.code_export, id = _MENU_EXPORT_CLASS)
        self.Bind(wx.EVT_MENU, self.code_export_as, id = _MENU_EXPORT_CLASS_AS)
        #view menu
        self.Bind(wx.EVT_MENU, self._evt_setting, id=_MENU_HIDE1UNDERSCORE)
        self.Bind(wx.EVT_MENU, self._evt_setting, id=_MENU_HIDE2UNDERSCORE)
        self.Bind(wx.EVT_MENU, self._evt_setting, id=_TOOL_AUTOREFRESH)
        self.Bind(wx.EVT_MENU, self._evt_setting, id=_TOOL_AUTOAPPLY)            
        self.Bind(wx.EVT_MENU, self.apply, id=_TOOL_APPLY)
        self.Bind(wx.EVT_MENU, self.refresh, id=_TOOL_REFRESH) 
        self.Bind(wx.EVT_MENU, self.view_source_code, id=_TOOL_VIEWSOURCE) 
        self.Bind(wx.EVT_MENU, self.open_shell, id=_TOOL_SHELL) 
        #help menu
        self.Bind(wx.EVT_MENU, self.show_help, id=_HELP_INFO)       
        self.Bind(wx.EVT_MENU, self.help_context, id=_HELP_CONTEXT)       

_TOOL_AUTOAPPLY = wx.NewId()
_TOOL_APPLY = wx.NewId()
_TOOL_AUTOREFRESH = wx.NewId()
_TOOL_REFRESH = wx.NewId()
_TOOL_VIEWSOURCE = wx.NewId()
_TOOL_SHELL = wx.NewId()
_MENU_HIDE1UNDERSCORE = wx.NewId()
_MENU_HIDE2UNDERSCORE = wx.NewId()
_MENU_SAVE = wx.NewId()
_MENU_SAVE_AS = wx.NewId()
_MENU_LOAD = wx.NewId()
_MENU_EXPORT_CLASS = wx.NewId()
_MENU_EXPORT_CLASS_AS = wx.NewId()
_MENU_EXPORT_OBJECT = wx.NewId()
_MENU_EXPORT_OBJECT_AS = wx.NewId()
_DUMMYID = wx.NewId()
_HELP_INFO = wx.NewId()
_HELP_CONTEXT = wx.NewId()

#settingDict contains correspondences between controls and setting fields
_settingDict = {_TOOL_AUTOAPPLY:"auto_apply", 
            _TOOL_AUTOREFRESH:"auto_refresh",
            _MENU_HIDE1UNDERSCORE:"hide_1_underscore",
            _MENU_HIDE2UNDERSCORE:"hide_2_underscore"
            }
