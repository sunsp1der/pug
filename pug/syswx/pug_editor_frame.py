import wx
import wx.aui
from wx.aui import AuiNotebook
from wx.py.editor import *

from pug.syswx.util import get_icon
        
class PugEditorNotebook( AuiNotebook):
    """A notebook containing a page for each editor."""

    def AddPage(*a,**kw):
        if "text" in kw:
            kw["caption"]=kw["text"]
            kw.pop("text")
        AuiNotebook.AddPage(*a, **kw)
        
class PugEditorFrame( EditorNotebookFrame):
    """Pug version of the py editor"""
    def __init__(self, parent=None, id=-1, title='Pug Python Editor',
                 pos=wx.DefaultPosition, size=(800, 600), 
                 style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE,
                 filename=None):
        """Create EditorNotebookFrame instance."""        
        self.notebook = None
        EditorNotebookFrame.__init__(self, parent, id, title, pos,
                             size, style, filename)
        self._defaultText = title        
        self.SetIcon(get_icon())                     
        if self.notebook:
            dispatcher.connect(receiver=self._editorChange,
                               signal='EditorChange', sender=self.notebook)

    def _setup(self):
        """_setup() with browser page"""
        self.notebook = PugEditorNotebook(parent=self)
        folder = wx.GetApp().get_project_folder()
        self.browser = wx.GenericDirCtrl(parent=self.notebook, 
                        dir=folder,
                        filter="Python files (*.py)|*.py|All files (*.*)|*.*")
        self.browser_tree = self.browser.GetTreeCtrl()
        self.browser_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnBrowserDClick)
        self.notebook.AddPage(page=self.browser, text="* Browser *",
                              select=True)
    
    def OnBrowserDClick(self, event):
        filename = self.browser.GetFilePath()
        self.bufferCreate(filename)
        
    def __createMenus(self):
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
        m.Append(ID_SAVE, '&Save... \tCtrl+S',
                 'Save file')
        m.Append(ID_SAVEAS, 'Save &As \tCtrl+Shift+S',
                 'Save file with new name')
        m.AppendSeparator()
        m.Append(ID_PRINT, '&Print... \tCtrl+P',
                 'Print file')
        m.AppendSeparator()
#        m.Append(ID_NAMESPACE, '&Update Namespace \tCtrl+Shift+N',
#                 'Update namespace for autocompletion and calltips')
        m.AppendSeparator()
        m.Append(ID_EXIT, 'E&xit\tCtrl+Q', 'Exit Program')

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
        m.Append(ID_TOGGLE_MAXIMIZE, '&Toggle Maximize\tF11', 'Maximize/Restore Application')
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
        m.Append(ID_AUTOCOMP_SINGLE, 'Include Single &Underscores\tCtrl+Shift+U',
                 'Include attibutes prefixed by a single underscore', wx.ITEM_CHECK)
        m.Append(ID_AUTOCOMP_DOUBLE, 'Include &Double Underscores\tCtrl+Shift+D',
                 'Include attibutes prefixed by a double underscore', wx.ITEM_CHECK)
        m = self.calltipsMenu = wx.Menu()
        m.Append(ID_CALLTIPS_SHOW, 'Show Call &Tips\tCtrl+Shift+T',
                 'Show call tips with argument signature and docstring', wx.ITEM_CHECK)
        m.Append(ID_CALLTIPS_INSERT, '&Insert Call Tips\tCtrl+Shift+I',
                 '&Insert Call Tips', wx.ITEM_CHECK)

        m = self.optionsMenu = wx.Menu()
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
        b.Append(self.helpMenu, '&Help')
        self.SetMenuBar(b)

        self.Bind(wx.EVT_MENU, self.OnFileNew, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnFileRevert, id=ID_REVERT)
        self.Bind(wx.EVT_MENU, self.OnFileClose, id=ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnFileSave, id=ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnFileUpdateNamespace, id=ID_NAMESPACE)
        self.Bind(wx.EVT_MENU, self.OnFilePrint, id=ID_PRINT)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
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
