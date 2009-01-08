import wx
import wx.lib.scrolledpanel as scrolled
import wx.richtext as rt

from pug.syswx.component_helpers import ComponentTreeCtrl
from pug.syswx.util import get_icon
from pug.component import component_method

class ComponentBrowseDlg(wx.Dialog):
    """ComponentBrowseDlg( parent, object=None, start_component=None): 
    
parent: parent window
object: browse components applicable to this object (None yields ALL)
start_component: start with view of this component
"""
    def __init__(self, parent, object=None, start_component=None):
        #HACK - had to use DD_DEFAULT_STYLE to make it sizeable
        wx.Dialog.__init__(self, parent, style = wx.DD_DEFAULT_STYLE,
                           title = 'Select A Component')
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetSize((840, 500))   
        self.SetIcon(get_icon())             
        self.component = None
        
        buttonSizer = wx.StdDialogButtonSizer()
        okayButton = wx.Button(self,wx.ID_OK)
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonSizer.AddButton(okayButton)
        buttonSizer.AddButton(cancelButton)
        buttonSizer.Realize()
        
        self.browser = ComponentBrowseWindow(self, object)
        if start_component:
            self.browser.select_component(start_component)
        
        sizer.Add(self.browser, 1, wx.EXPAND | wx.SOUTH, 10)        
        sizer.Add(buttonSizer, 0, wx.EXPAND | wx.SOUTH | wx.EAST, 10)
        okayButton.Bind(wx.EVT_BUTTON, self.on_ok)
        
    def on_ok(self, event):
        self.component = self.browser.currentComponent
        event.Skip()
        
class ComponentBrowseFrame(wx.Frame):
    """ComponentBrowseFrame(...)
    
(parent, object=None, start_component=None,title='Component Browser'): 
    
parent: parent window
object: browse components applicable to this object (None yields ALL)
start_component: start with view of this component
title: the window title
"""
    def __init__(self, parent=None, object=None, start_component=None, 
                 title="Component Browser"):
        #HACK - had to use DD_DEFAULT_STYLE to make it sizeable
        wx.Frame.__init__(self, parent, style = wx.DD_DEFAULT_STYLE,
                           title = title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetSize((840, 450))        
        self.SetIcon(get_icon())             
        
        self.browser = ComponentBrowseWindow(self, object)
        if start_component:
            self.browser.select_component(start_component)
        
        sizer.Add(self.browser, 1, wx.EXPAND | wx.SOUTH, 10)        
                
class ComponentBrowseWindow(wx.SplitterWindow):
    """ComponentBrowseWindow( parent, object)

parent: parent window
object: browse components applicable to this object (None yields ALL)

Shows all available components and info about each. A splitter window with a
tree on the left and info on the right.
"""
    def __init__(self, parent, object):
        wx.SplitterWindow.__init__(self, parent)
        self.MinSize = (534, 87)
        tree = ComponentTreeCtrl(self)
        tree.CreateComponentTree(object)
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.tree = tree
        
        infowin = scrolled.ScrolledPanel(self, style=wx.BORDER_SUNKEN)
        infosizer = wx.BoxSizer(wx.VERTICAL)
        infowin.SetSizer(infosizer)
        infowin.SetAutoLayout(1)
        self.infosizer = infosizer
        self.infowin = infowin
        self.SplitVertically(tree, infowin, 207)
        self.currentItem = None
        self.currentComponent = None

    def on_sel_changed(self, evt):
        """on_sel_changed(): Display component info"""
        #item = self.tree.GetComponentItemByPosition(evt.GetPosition())
        item = self.tree.GetSelection()
        if item and item is not self.currentItem:
            self.currentItem = item
            self.currentComponent = self.tree.GetItemPyData(item)
            if self.currentComponent:
                self.display_component( self.currentComponent)
        evt.Skip()
            
    def select_component(self, component):
        item = self.tree.FindItemByData( component) 
        if item:
            self.currentItem = item
            self.currentComponent = component
            self.tree.SelectItem(item) 
            self.display_component(component)          
            
    def display_component(self, component):
        """Create text to describe component"""
        #TODO: this is just an ugly, hacked version. Need a nice display format
        #title
        self.infowin.Freeze()
        if component is None:
            return
        self.infosizer.Clear(True)
        textlist = []
        textlist.append(component.__name__)
        textlist.append('\n\n')
        textlist.append(component.__doc__)
        textlist.append('\n\n')        
        textlist+=['Set: ',component._set,'\n']
        textlist+=['Type: ',component._type,'\n']
        textlist+=['For Class: ',]
        c = 0
        for cls in component._class_list:
            if c:
                textlist.append('           ')
            textlist+=[cls.__module__,'.',cls.__name__,'\n']
        textlist.append('\n')
        textlist+=['Attributes:']
        text=''.join(textlist)
        text = wx.StaticText(self.infowin, -1, text)
        self.infosizer.Add(text,0,wx.WEST,5)
        for item in component._attribute_list:
            textlist = []
            textlist+=['\n',item[0],': (Default=']
            textlist+=[repr(getattr(component, item[0])),')']
            text=''.join(textlist)
            text = wx.StaticText(self.infowin, -1, text)
            self.infosizer.Add(text,0,wx.WEST,15)
            text = wx.StaticText(self.infowin, -1, item[1])
            self.infosizer.Add(text,0,wx.WEST,35)
        text = wx.StaticText(self.infowin, -1, '\nMethods:\n')
        self.infosizer.Add(text,0,wx.WEST,5)
        for item in dir(component):
            if isinstance(getattr(component, item), component_method):
                text = ''.join([item,':'])
                text = wx.StaticText(self.infowin, -1, text)
                self.infosizer.Add(text,0,wx.WEST,15)
                text = wx.StaticText(self.infowin, -1, 
                                     getattr(component,item).__doc__)
                self.infosizer.Add(text,0,wx.WEST,35)
        self.infosizer.Layout()
        self.infosizer.MinSize = self.infosizer.Size
        self.infowin.SetupScrolling()
        self.infowin.Thaw()