import os
import weakref

import wx
from wx.lib.agw import aui
#from wx.aui import AuiNotebook
from wx.py.editor import *
from wx.py.frame import *

from pug.util import start_file
from pug.syswx.util import get_icon
from pug.syswx.file_tree import FileTree
        
class PugEditorNotebook( aui.AuiNotebook):
    """A notebook containing a page for each editor."""
    def AddPage(*a,**kw):
        if "text" in kw:
            kw["caption"]=kw["text"]
            kw.pop("text")
        aui.AuiNotebook.AddPage(*a, **kw)
        
class CodeEditorFrame( EditorNotebookFrame):
    """CodeEditorFrame(self, parent=None, id=-1, title='Pug Code Editor',
                 pos=wx.DefaultPosition, size=(800, 600), 
                 style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE,
                 filename=None, project_only=False, components_folder=None,
                 browser_root=".", browser_filter=("*.py","*.pyw"))

filename: file to open for editing
project_only: files not in the pug project folder will be readonly by default
components_folder: any files with 'components' in their path will have their
    default path changed to this folder when they are opened for editing.
browser_root: if not None will show a file browser with root in the given folder
browser_filter: filter for browser files          
Pug version of the py editor."""
    def __init__(self, parent=None, id=-1, title='Pug Python Editor',
                 pos=wx.DefaultPosition, size=(800, 600), 
                 style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE,
                 filename=None, project_only=False, components_folder=None,
                 browser_root=".", browser_filter = ("*.py","*.pyw")):
        """Create EditorNotebookFrame instance."""        
        self.notebook = None
        self.project_only = project_only
        self.components_folder = components_folder
        EditorNotebookFrame.__init__(self, parent, id, title, pos,
                             size, style, filename)
        dispatcher.connect(receiver=self._editorChange,
                               signal='EditorChange', sender=self.notebook)
        self.notebook.Bind(wx.EVT_IDLE, self.OnIdle)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, 
                           self.OnPageChanged, 
                           id=self.notebook.GetId())        
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.PageClose,
                           id=self.notebook.GetId())
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        # override default menus
        self._createMenus()
        # setup look
        self.SetStatusText(title)        
        self.SetIcon(get_icon())     
        if browser_root is not None:
            self.browser = FileTree( self.notebook, 
                                     rootfolder=browser_root,
                                     file_filter=browser_filter) 
        self.browser.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnBrowserDClick)
        self.notebook.AddPage(page=self.browser, text="* Browser *",
                              select=True)
        
    def _setup(self):
        """_setup() with browser page"""
        self.notebook = PugEditorNotebook(parent=self,style=aui.AUI_NB_TAB_FLOAT)

    def OnIdle(self, event):
        """Event handler for idle time."""
        self._updateStatus()
        self._updateTabText()
        event.Skip()
            
    def OnPageChanged(self, event):
        """Page changed event handler."""
        new = event.GetSelection()
        window = self.notebook.GetPage(new)
        if hasattr(window,"editor"):
            dispatcher.send(signal='EditorChange', sender=self.notebook,
                            editor=window.editor)
        window.SetFocus()
  
    def _updateTabText(self, pagenum=None):
        """Show current buffer display name on all but first tab."""
        if pagenum is None:
            pagenum = self.notebook.GetSelection()
            try:
                page = self.notebook.GetPage(pagenum)
            except:
                return
        else:
            page = self.notebook.GetPage(pagenum)
        if not hasattr(page,"buffer"):
            return
        changed = ' **'
        text = self.notebook.GetPageText(pagenum)
        if text.endswith(changed):
            name = text[:-len(changed)]
        else:
            name = text
        if page.buffer.hasChanged():
            name = name + changed
        if name != text:
            self.notebook.SetPageText(pagenum, name)

    def PageClose(self, event):
        id = event.Int
        if id == 0:
            event.Veto()
        page = self.notebook.GetPage(id)
        if hasattr(page, "buffer"):
            if page.buffer.hasChanged():
                cancel = self.bufferSuggestSave()
                if cancel:
                    event.Veto()
                    return
            del self.buffers[page.buffer.id]
        
    def on_show_object(self, object):
        "Callback from pug.App"
        for pagenum in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(pagenum)
            try:
                if page.pug_view_key == object:
                    self.notebook.SetSelection(pagenum)
                    return
            except:
                continue
            
    def open_shell(self, rootObject=None, rootLabel=None, locals=None, 
                   clean_tools=True, pug_view_key=None, **kw):
        """open_shell(rootObject=None, rootLabel=None, locals=None, 
                   clean_tools=True, pug_view_key=None, **kw)
                   
rootObject: the root object of shell tree. A dict of objects also works nicely.
rootLabel: the label for the root object
locals: the locals available in the shell
clean_tools: if True, remove the Display, Calltip, and Dispatcher pages
pug_view_key: this is the main viewing object for this frame. Used by pug to
    determine if duplicate shells are being opened. Defaults to rootObject.
    It will be converted to a tuple: (weakref.ref(pug_view_key),"shell") and
    stored as the 'pug_view_key' field of the shell frame.
other kw args: sent to Crust()
"""
        app = wx.GetApp()
        if pug_view_key is None:
            pug_view_key = rootObject
        try:
            pug_key = (weakref.ref(pug_view_key),"shell")
        except:
            pug_key = None
        else:
            if app.show_object_frame(pug_key):
                # we already have a shell open for this object
                return None
        shell = crust.Crust(self.notebook, locals=locals, rootObject=rootObject, 
                            rootLabel=rootLabel,**kw)
        if clean_tools:
            shell.notebook.RemovePage(4)
            shell.notebook.RemovePage(2)
            shell.notebook.RemovePage(1)
        if pug_key:
            shell.pug_view_key = pug_key
            app.frame_viewing(self, pug_key)
        if rootLabel:
            text = "Shell:"+rootLabel
        else:
            text = "-Shell-"
        self.notebook.AddPage(page=shell, text=text, select=True)
        self.setEditor( shell.editor)
        wx.CallAfter( shell.editor.SetFocus)
        self.Show()
        return shell
    
    def open_code_file(self, filename):
        """open_code_file: open filepath for editing"""
        self.bufferCreate( filename)
        self.Show()
       
    def bufferCreate(self, filename):
        """Create new buffer. No duplicate buffers or names..."""
        # no duplicate buffers
        filename = os.path.realpath(filename)
        app = wx.GetApp()
        pug_key = (filename, "code")
        if app.show_object_frame(pug_key):
            return
        buffer = Buffer()
        panel = wx.Panel(parent=self.notebook, id=-1)
        panel.buffer = buffer # track this for ease
        panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: x)        
        editor = Editor(parent=panel)
        panel.editor = editor
        panel.pug_view_key = pug_key
        app.frame_viewing( self, pug_key)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(editor.window, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        sizer.Layout()
        buffer.addEditor(editor)
        buffer.open(filename)
        self.setEditor(editor)
        # no duplicate tab labels
        self.notebook.Freeze()
        tab_label = self.buffer.name
        pages = self.notebook.GetPageCount()
#        if pages > 1:
#            self.notebook._curpage = pages - 1
#        else:
#            tab = self.notebook.GetActiveTabCtrl()
        for pagenum in range(pages):
            page = self.notebook.GetPage(pagenum)
            if not hasattr(page,"buffer"):
                continue
            if page.buffer.name == self.buffer.name:
                tab_label = self.GetDetailedBufferName( buffer)
                self.notebook.SetPageText(pagenum, 
                                      self.GetDetailedBufferName(page.buffer))
                break
        self.notebook.AddPage(page=panel, text=tab_label, select=True)
#        if pages == 1:
#            # first editor... do split
#            self.notebook.Split(0,wx.LEFT)
#            size = tab.GetSize()
#            page = self.notebook.GetPage(0)
#            frame = self.notebook.GetTabFrameFromWindow(page)
#            pane = self.notebook._mgr.GetAllPanes()[2]
#            pane.rect[3] = pane.rect[3]/2
#            #pane.SetSize(50,-1)
#            tab.SetSize((50,size[1]))
#            self.notebook._mgr.Update()
#            import wx.lib.inspection as fred
#            fred.InspectionTool().Show()

#            frame.GetNotebook().GetPage(1).SetSize([size[0]/2,size[1]])
        if (self.project_only and \
                    app.get_project_folder() not in filename) and not\
                    (self.components_folder and 'components' in \
                     self.buffer.doc.filedir):
            editor.window.SetReadOnly(True)
        self.notebook.Thaw()
        return panel

    def OnBrowserDClick(self, event):
        filename = self.browser.GetFilePath()
        if os.path.isfile(filename):
            # it's not a folder
            self.bufferCreate(filename)

    def testComponentRedirect(self, path):
        """True if self.components_folder is True and 'components' is in path
and path is not inside the project folder"""
        return self.components_folder and 'components' in path and\
                    wx.GetApp().get_project_folder() not in path
                
    def bufferSave(self, buffer=None):
        """Save buffer to its file. Redirect components if necessary"""
        if buffer is None:
            buffer = self.buffer
        if self.testComponentRedirect( buffer.doc.filedir):
            cancel = self.bufferSaveAs( buffer)
        elif buffer.doc.filepath:
            self.buffer.save()
            cancel = False
        else:
            cancel = self.bufferSaveAs( buffer)
        return cancel

    def bufferSaveAs(self, buffer=None):
        """Save buffer to a new filename. Redirect components if necessary"""
        if buffer is None:
            buffer = self.buffer
        if buffer.editor:
            for pagenum in range(self.notebook.GetPageCount()):
                page = self.notebook.GetPage(pagenum)
                if hasattr(page, "editor") and page.editor == buffer.editor:
                    self.notebook.SetSelection(pagenum)
                    break
        if self.testComponentRedirect(buffer.doc.filedir):
            result = saveSingle(parent=self,
                                directory=self.components_folder,
                                filename=buffer.doc.filename)
        else:
            filedir = ''
            if buffer.doc.filedir:
                filedir = self.buffer.doc.filedir
            result = saveSingle(parent=self,
                                directory=filedir)
        if result.path:
            buffer.saveAs(result.path)
            cancel = False
        else:
            cancel = True
        return cancel    

    def OnUpdateMenu(self, event):
        Frame.OnUpdateMenu(self, event)
            
    def GetDetailedBufferName(self, buffer):
        path, firstdir = os.path.split(buffer.doc.filedir)
        return os.path.join( firstdir, buffer.doc.filename)
            
    def OnShell(self, event):
        rootObject = wx.GetApp().get_project_object()
        rootLabel = "ProjectObject"
        locals = {rootLabel:rootObject}
        self.open_shell(rootObject, rootLabel, locals)
        
    def OnFileSaveAll(self, event=None):
        for pagenum in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(pagenum)
            if hasattr(page,"buffer") and page.buffer.hasChanged():
                self.bufferSave( page.buffer)
                
    def OnQuit(self, event):
        wx.GetApp().get_project_object().quit()

    def OnExit(self, event):
        self.Hide()
        if event.CanVeto():
            event.Veto()
        
    def OnReadOnly(self, event):
        self.buffer.editor.window.SetReadOnly(event.IsChecked())
        
    def OnProjectFolder(self, event):
        return start_file(wx.GetApp().get_project_folder())
                    
    def OnUpdateMenu(self, event):        
        Frame.OnUpdateMenu(self,event)
        win = wx.Window.FindFocus()
        id = event.GetId()
        event.Enable(True)
        try:
            if id == ID_READONLY:
                event.Check(win.GetReadOnly())
        except AttributeError:
            event.Enable(False)
                    
    def _createMenus(self):
        # File Menu
        m = self.fileMenu = wx.Menu()
        m.Append(ID_NEW, '&New \tCtrl+N',
                 'New file')
        m.Append(ID_OPEN, '&Open... \tCtrl+O',
                 'Open file')
        m.AppendSeparator()
        m.Append(ID_REVERT, '&Revert \tCtrl+R',
                 'Revert to last saved version')
        m.Append(ID_CLOSE, '&Close \tCtrl+W',
                 'Close file')
        m.AppendSeparator()
        m.Append(ID_SAVE, '&Save \tCtrl+S',
                 'Save file')
        m.Append(ID_SAVEAS, 'Save &As...\tCtrl+A',
                 'Save file with new name')
        m.Append(ID_SAVEALL, 'Save A&ll \tCtrl+Shift+S',
                 'Save all files')
        m.AppendSeparator()
        m.Append(ID_PRINT, '&Print... \tCtrl+P',
                 'Print file')
        m.AppendSeparator()
        m.Append(ID_SHELL, 'Project S&hell \tCtrl+H', 'Open project shell tab')
        m.Append(ID_PROJECTFOLDER, 'Browse Project &Folder \tCtrl+F', 
                 "Open the project's folder in a browser")
#        m.Append(ID_NAMESPACE, '&Update Namespace \tCtrl+Shift+N',
#                 'Update namespace for autocompletion and calltips')
        m.AppendSeparator()
        m.Append(ID_EXIT, 'E&xit', 'Hide Editor')
        m.Append(ID_QUIT, '&Quit\tCtrl+Q', 'Quit Pig')

        # Edit
        m = self.editMenu = wx.Menu()
        m.Append(ID_UNDO, '&Undo \tCtrl+Z',
                 'Undo the last action')
        m.Append(ID_REDO, '&Redo \tCtrl+Y',
                 'Redo the last undone action')
        m.AppendSeparator()
        m.Append(ID_CUT, 'Cu&t \tCtrl+X',
                 'Cut the selection')
        m.Append(ID_COPY, '&Copy \tCtrl+C',
                 'Copy the selection')
        m.Append(ID_COPY_PLUS, 'Cop&y Plus \tCtrl+Shift+C',
                 'Copy the selection - retaining prompts')
        m.Append(ID_PASTE, '&Paste \tCtrl+V', 'Paste from clipboard')
        m.Append(ID_PASTE_PLUS, 'Past&e Plus \tCtrl+Shift+V',
                 'Paste and run commands')
        m.AppendSeparator()
        m.Append(ID_CLEAR, 'Cle&ar',
                 'Delete the selection')
        m.Append(ID_SELECTALL, 'Select A&ll \tCtrl+A',
                 'Select all text')
        m.AppendSeparator()
#        m.Append(ID_EMPTYBUFFER, 'E&mpty Buffer...',
#                 'Delete all the contents of the edit buffer')
        m.Append(ID_FIND, '&Find Text... \tCtrl+F',
                 'Search for text in the edit buffer')
        m.Append(ID_FINDNEXT, 'Find &Next \tF3',
                 'Find next/previous instance of the search text')

        # View
        m = self.viewMenu = wx.Menu()
        m.Append(ID_WRAP, '&Wrap Lines\tCtrl+Shift+W',
                 'Wrap lines at right edge', wx.ITEM_CHECK)
        m.Append(ID_SHOW_LINENUMBERS, '&Show Line Numbers\tCtrl+Shift+L', 'Show Line Numbers', wx.ITEM_CHECK)
#        m.Append(ID_TOGGLE_MAXIMIZE, '&Toggle Maximize\tF11', 'Maximize/Restore Application')
        if hasattr(self, 'ToggleTools'):
            m.Append(ID_SHOWTOOLS,
                     'Show &Tools\tF4',
                     'Show the filling and other tools', wx.ITEM_CHECK)

        # Options
        m = self.autocompMenu = wx.Menu()
        m.Append(ID_AUTOCOMP_SHOW, 'Show &Auto Completion\tCtrl+Shift+A',
                 'Show auto completion list', wx.ITEM_CHECK)
        m.Append(ID_AUTOCOMP_MAGIC, 'Include &Magic Attributes\tCtrl+Shift+M',
                 'Include attributes visible to __getattr__ and __setattr__',
                 wx.ITEM_CHECK)
        m.Append(ID_AUTOCOMP_SINGLE, 
                 'Include Single &Underscores\tCtrl+Shift+U',
                 'Include attibutes prefixed by a single underscore', 
                 wx.ITEM_CHECK)
        m.Append(ID_AUTOCOMP_DOUBLE, 
                 'Include &Double Underscores\tCtrl+Shift+D',
                 'Include attibutes prefixed by a double underscore', 
                 wx.ITEM_CHECK)
        m = self.calltipsMenu = wx.Menu()
        m.Append(ID_CALLTIPS_SHOW, 'Show Call &Tips\tCtrl+Shift+T',
                 'Show call tips with argument signature and docstring', 
                 wx.ITEM_CHECK)
        m.Append(ID_CALLTIPS_INSERT, '&Insert Call Tips\tCtrl+Shift+I',
                 '&Insert Call Tips', wx.ITEM_CHECK)

        m = self.optionsMenu = wx.Menu()
        m.Append(ID_READONLY, '&Read Only','File cannot be changed',
                 wx.ITEM_CHECK)
        m.AppendMenu(ID_AUTOCOMP, '&Auto Completion', self.autocompMenu,
                     'Auto Completion Options')
        m.AppendMenu(ID_CALLTIPS, '&Call Tips', self.calltipsMenu,
                     'Call Tip Options')
                
        if wx.Platform == "__WXMAC__":
            m.Append(ID_USEAA, '&Use AntiAliasing',
                     'Use anti-aliased fonts', wx.ITEM_CHECK)
#            
#        m.AppendSeparator()

#        self.historyMenu = wx.Menu()
#        self.historyMenu.Append(ID_SAVEHISTORY, '&Autosave History',
#                 'Automatically save history on close', wx.ITEM_CHECK)
#        self.historyMenu.Append(ID_SAVEHISTORYNOW, '&Save History Now',
#                 'Save history')
#        self.historyMenu.Append(ID_CLEARHISTORY, '&Clear History ',
#                 'Clear history')
#        m.AppendMenu(-1, "&History", self.historyMenu, "History Options")
#
#        self.startupMenu = wx.Menu()
##        self.startupMenu.Append(ID_EXECSTARTUPSCRIPT,
##                                'E&xecute Startup Script',
##                                'Execute Startup Script', wx.ITEM_CHECK)
##        self.startupMenu.Append(ID_EDITSTARTUPSCRIPT,
##                                '&Edit Startup Script...',
##                                'Edit Startup Script')
##        m.AppendMenu(ID_STARTUP, '&Startup', self.startupMenu, 'Startup Options')
#
#        self.settingsMenu = wx.Menu()
#        self.settingsMenu.Append(ID_AUTO_SAVESETTINGS,
#                                 '&Auto Save Settings',
#                                 'Automatically save settings on close', wx.ITEM_CHECK)
#        self.settingsMenu.Append(ID_SAVESETTINGS,
#                                 '&Save Settings',
#                                 'Save settings now')
#        self.settingsMenu.Append(ID_DELSETTINGSFILE,
#                                 '&Revert to default',
#                                 'Revert to the default settings')
#        m.AppendMenu(ID_SETTINGS, '&Settings', self.settingsMenu, 'Settings Options')           
#
#        m = self.helpMenu = wx.Menu()
#        m.Append(ID_HELP, '&Help\tF1', 'Help!')
#        m.AppendSeparator()
#        m.Append(ID_ABOUT, '&About...', 'About this program')
        b = self.menuBar = wx.MenuBar()
        b.Append(self.fileMenu, '&File')
        b.Append(self.editMenu, '&Edit')
        b.Append(self.viewMenu, '&View')
        b.Append(self.optionsMenu, '&Options')
#        b.Append(self.helpMenu, '&Help')
        self.SetMenuBar(b)

        self.Bind(wx.EVT_MENU, self.OnFileNew, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnFileRevert, id=ID_REVERT)
        self.Bind(wx.EVT_MENU, self.OnFileClose, id=ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnFileSave, id=ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAll, id=ID_SAVEALL)
        self.Bind(wx.EVT_MENU, self.OnFileUpdateNamespace, id=ID_NAMESPACE)
        self.Bind(wx.EVT_MENU, self.OnFilePrint, id=ID_PRINT)
        self.Bind(wx.EVT_MENU, self.OnShell, id=ID_SHELL)
        self.Bind(wx.EVT_MENU, self.OnProjectFolder, id=ID_PROJECTFOLDER)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=ID_QUIT)
        self.Bind(wx.EVT_MENU, self.OnUndo, id=ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnCut, id=ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnCopyPlus, id=ID_COPY_PLUS)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=ID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnPastePlus, id=ID_PASTE_PLUS)
        self.Bind(wx.EVT_MENU, self.OnClear, id=ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, id=ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnEmptyBuffer, id=ID_EMPTYBUFFER)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnReadOnly, id=ID_READONLY)
        self.Bind(wx.EVT_MENU, self.OnAutoCompleteShow, id=ID_AUTOCOMP_SHOW)
        self.Bind(wx.EVT_MENU, self.OnAutoCompleteMagic, id=ID_AUTOCOMP_MAGIC)
        self.Bind(wx.EVT_MENU, self.OnAutoCompleteSingle, id=ID_AUTOCOMP_SINGLE)
        self.Bind(wx.EVT_MENU, self.OnAutoCompleteDouble, id=ID_AUTOCOMP_DOUBLE)
        self.Bind(wx.EVT_MENU, self.OnCallTipsShow, id=ID_CALLTIPS_SHOW)
        self.Bind(wx.EVT_MENU, self.OnCallTipsInsert, id=ID_CALLTIPS_INSERT)
        self.Bind(wx.EVT_MENU, self.OnWrap, id=ID_WRAP)
        self.Bind(wx.EVT_MENU, self.OnUseAA, id=ID_USEAA)
        self.Bind(wx.EVT_MENU, self.OnToggleMaximize, id=ID_TOGGLE_MAXIMIZE)
        self.Bind(wx.EVT_MENU, self.OnShowLineNumbers, id=ID_SHOW_LINENUMBERS)
        self.Bind(wx.EVT_MENU, self.OnAutoSaveSettings, id=ID_AUTO_SAVESETTINGS)
        self.Bind(wx.EVT_MENU, self.OnSaveHistory, id=ID_SAVEHISTORY)
        self.Bind(wx.EVT_MENU, self.OnSaveHistoryNow, id=ID_SAVEHISTORYNOW)
        self.Bind(wx.EVT_MENU, self.OnClearHistory, id=ID_CLEARHISTORY)
        self.Bind(wx.EVT_MENU, self.OnSaveSettings, id=ID_SAVESETTINGS)
        self.Bind(wx.EVT_MENU, self.OnDelSettingsFile, id=ID_DELSETTINGSFILE)
        self.Bind(wx.EVT_MENU, self.OnEditStartupScript, id=ID_EDITSTARTUPSCRIPT)
        self.Bind(wx.EVT_MENU, self.OnExecStartupScript, id=ID_EXECSTARTUPSCRIPT)
        self.Bind(wx.EVT_MENU, self.OnFindText, id=ID_FIND)
        self.Bind(wx.EVT_MENU, self.OnFindNext, id=ID_FINDNEXT)
        self.Bind(wx.EVT_MENU, self.OnToggleTools, id=ID_SHOWTOOLS)

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_NEW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_OPEN)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_REVERT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_CLOSE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_NAMESPACE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_PRINT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_COPY_PLUS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_PASTE_PLUS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_CLEAR)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SELECTALL)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_EMPTYBUFFER)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_READONLY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_AUTOCOMP_SHOW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_AUTOCOMP_MAGIC)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_AUTOCOMP_SINGLE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_AUTOCOMP_DOUBLE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_CALLTIPS_SHOW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_CALLTIPS_INSERT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_WRAP)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_USEAA)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SHOW_LINENUMBERS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_AUTO_SAVESETTINGS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SAVESETTINGS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_DELSETTINGSFILE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_EXECSTARTUPSCRIPT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SAVEHISTORY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SAVEHISTORYNOW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_CLEARHISTORY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_EDITSTARTUPSCRIPT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_FIND)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_FINDNEXT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateMenu, id=ID_SHOWTOOLS)
        
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        self.Bind(wx.EVT_FIND, self.OnFindNext)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        
ID_QUIT = wx.NewId()
ID_SHELL = wx.NewId()
ID_READONLY = wx.NewId()
ID_SAVEALL = wx.NewId()
ID_PROJECTFOLDER = wx.NewId()