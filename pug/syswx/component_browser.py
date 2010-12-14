import types

import wx
import wx.lib.scrolledpanel as scrolled
import wx.richtext as rt

from pug.syswx.component_helpers import ComponentTreeCtrl
from pug.syswx.util import get_icon
from pug.component import component_method

class ComponentAddDlg(wx.Dialog):
    """ComponentAddDlg( parent, object, start_component=None): 

This dialog is used to add components to object
parent: parent window
object: object to add to on select. Only show components available to this obj.
start_component: start with view of this component
"""
    def __init__(self, parent, object=None, start_component=None):
        #HACK - had to use DD_DEFAULT_STYLE to make it sizeable
        wx.Dialog.__init__(self, parent, style = wx.DD_DEFAULT_STYLE,
                           title = 'Select A Component To Add')
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetSize((633, 455))   
        self.SetIcon(get_icon())             
        self.component = None
        
        buttonSizer = wx.StdDialogButtonSizer()
        addButton = wx.Button(self,wx.ID_OK,label="Add")
        cancelButton = wx.Button(self,wx.ID_CANCEL)
        buttonSizer.AddButton(addButton)
        buttonSizer.AddButton(cancelButton)
        buttonSizer.Realize()
        
        self.browser = ComponentBrowseWindow(self, object)
        if start_component:
            self.browser.select_component(start_component)
        self.browser.tree.ExpandRecent()
        
        sizer.Add(self.browser, 1, wx.EXPAND | wx.SOUTH, 10)        
        sizer.Add(buttonSizer, 0, wx.EXPAND | wx.SOUTH | wx.WEST, 10)
        addButton.Bind(wx.EVT_BUTTON, self.on_add)
        self.browser.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.item_dclicked)
        
    def item_dclicked(self, event):
        self.component = self.browser.currentComponent
        if self.component:
            self.EndModal( wx.ID_OK)    
        
    def on_add(self, event):
        self.component = self.browser.currentComponent
        event.Skip()
        
class ComponentPickDlg(wx.Dialog):
    """ComponentPickDlg( parent, object=None, start_component=None): 
    
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
        self.SetSize((633,455))   
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
        self.SetSize((633, 455))        
        self.SetIcon(get_icon())             
        
        self.browser = ComponentBrowseWindow(self, object)
        if start_component:
            self.browser.select_component(start_component)
        
        sizer.Add(self.browser, 1, wx.EXPAND | wx.SOUTH, 1)        
                
class ComponentInfoWin(scrolled.ScrolledPanel):
    """ComponentInfoWin( parent, ScrolledPanel args...)
    
A basic text display of a components features...
"""                
    def __init__(self, *a, **kw):
        kw.setdefault('style',wx.BORDER_SUNKEN)
        scrolled.ScrolledPanel.__init__( self, *a, **kw)
        self.infosizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.infosizer)
        self.SetAutoLayout(1)

    def display_component(self, component):
        """Create text to describe component"""
        #TODO: this is just an ugly, hacked version. Need a nice display format
        #title
        if component is None:
            return
        self.Freeze()
        self.infosizer.Clear(True)
        textlist = []
        textlist.append(component.__name__)
        textlist.append('\n\n')
        if component.__doc__:
            textlist.append(component.__doc__)
            textlist.append('\n\n')        
        if component._set:
            textlist+=['Set: ',component._set,'\n']
        if component._type:
            textlist+=['Type: ',component._type,'\n']
        if component._class_list:
            textlist+=['For Class: ',]
            c = 0
            for cls in component._class_list:
                if c:
                    textlist.append('           ')
                textlist+=[cls.__name__,
                           ' (',cls.__module__,'.',cls.__name__,')\n']
        if component._field_list:
            textlist.append('\n')
            textlist+=['Fields:']
            text=''.join(textlist)
            text = wx.StaticText(self, -1, text)
            self.infosizer.Add(text,0,wx.WEST,5)
            dummy = component()
            for item in component._field_list:
                textlist = []
                textlist+=['\n',item[0],': (Default=']
                textlist+=[repr(getattr(dummy, item[0])),')']
                text=''.join(textlist)
                text = wx.StaticText(self, -1, text)
                self.infosizer.Add(text,0,wx.WEST,15)
                doc = ''
                if len(item) > 1:
                    if type(item[1]) in types.StringTypes:
                        doc = item[1]
                    elif len(item) > 2:
                        doc = item[2].get('doc', '')
                text = wx.StaticText(self, -1, doc)
                self.infosizer.Add(text,0,wx.WEST,35)
        text = wx.StaticText(self, -1, '\nMethods:')
        self.infosizer.Add(text,0,wx.WEST,5)
        for item in dir(component):
            attr = getattr(component, item)
            if isinstance(attr, component_method):
                text = ''.join(['\n',item,':'])
                text = wx.StaticText(self, -1, text)
                self.infosizer.Add(text,0,wx.WEST,15)
                if attr.__doc__:
                    text = wx.StaticText(self, -1, 
                                     attr.__doc__)
                    self.infosizer.Add(text,0,wx.WEST,35)
        self.infosizer.Layout()
        self.infosizer.MinSize = self.infosizer.Size
        self.SetupScrolling()
        if self.IsFrozen():
            self.Thaw()        
        
class ComponentBrowseWindow(wx.SplitterWindow):
    """ComponentBrowseWindow( parent, object=None, show_current=True)

parent: parent window
object: browse components applicable to this object (None yields ALL)
show_current: if this is True and object is not None, show a window with 
    object's current components below the component tree

Shows all available components and info about each. A splitter window with a
tree on the left and info on the right.
"""
    def __init__(self, parent, object=None, show_current=True):
        wx.SplitterWindow.__init__(self, parent)
        self.MinSize = (534, 87)
#        panel = wx.Panel(self)
#        sizer = wx.BoxSizer(wx.VERTICAL)
#        panel.SetSizer( sizer)
        
        # left
        #  tree
        tree = ComponentTreeCtrl(self)
        tree.CreateComponentTree(object)
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.tree = tree
#        sizer.Add(tree)#, 4, wx.EXPAND)
        #  current
#        if show_current and object is not None:
#            self.current = wx.ListBox(self, style=wx.LB_SINGLE)
#            self.current.Bind(wx.EVT_LISTBOX, self.current_click)
#            self.current.Bind(wx.EVT_LISTBOX_DCLICK, self.current_dclick)
#            sizer.Add(self.current, 1, wx.EXPAND)
#            components = object.components.get()    
#            components.reverse()       
#            for component in components:
#                label = component.__class__.__name__
#                if component.gname:
#                    label = label + ' (' + component.gname + ')'               
#                self.current.Insert(label, 0, component)
        # right
        infowin = ComponentInfoWin(self)
        self.infowin = infowin
        self.SplitVertically(tree, infowin, 180)
        self.currentItem = None
        self.currentComponent = None
        
    def current_click(self, evt):
        print "click"

    def current_dclick(self, evt):
        print "dclick"

    def on_sel_changed(self, evt):
        """on_sel_changed(): Display component info"""
        #item = self.tree.GetComponentItemByPosition(evt.GetPosition())
        item = self.tree.GetSelection()
        if item and item is not self.currentItem:
            self.currentItem = item
            self.currentComponent = self.tree.GetItemPyData(item)
            if self.currentComponent:
                self.infowin.display_component( self.currentComponent)
        evt.Skip()
            
    def select_component(self, component):
        item = self.tree.FindItemByData( component) 
        if item:
            self.currentItem = item
            self.currentComponent = component
            self.tree.SelectItem(item) 
            self.infowin.display_component(component)          
    