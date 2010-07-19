"""components.py - component viewer attribute gui"""

import gc

import wx
import wx.lib.buttons as buttons

from pug.syswx.wxconstants import *
from pug.syswx.pugbutton import PugButton
from pug.syswx.agui_label_sizer import AguiLabelSizer
from pug.syswx.component_helpers import ComponentAddTree, ComponentList
from pug.syswx.attributeguis.base import Base
from pug.syswx.component_browser import ComponentBrowseDlg

# TODO: make it fold up everything beneath it

class Components (Base):
    """Component attribute gui with features for adding, removing, editing
    
Components(attribute, window, aguidata, **kwargs)
attribute: name of component attribute (normally 'components')
window: the parent pugFrame
aguidata: {
    see Base for possiblities
    }

For kwargs optional arguments, see the Base attribute GUI
"""
    expanded = False
    object = None
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        #label
        label = wx.Panel(window, style=0)
#        if not hasattr(self, 'defaultBackgroundColor'):
#            defaultBackgroundColor = label.GetBackgroundColour()
#            r = defaultBackgroundColor[0] - 10
#            g = defaultBackgroundColor[1] - 10
#            b = defaultBackgroundColor[2] - 10
#            if r < 0: r = 0
#            if g < 0: g = 0
#            if b < 0: b = 0
#            defaultBackgroundColor.Set(r,g,b)
#            self.__class__.defaultBackgroundColor = defaultBackgroundColor
        labelAreaSizer = wx.BoxSizer(orient=wx.VERTICAL)
        textSizer = AguiLabelSizer(parent=label, line=False)
        labelAreaSizer.AddSizer(textSizer, 0, wx.TOP, 1)
        availSizer = AguiLabelSizer(parent=label, line=True, label='available:')
        availSizer.textCtrl.SetWindowStyleFlag(wx.TE_RIGHT)
        availSizer.textCtrl.SetForegroundColour('gray')
        labelAreaSizer.AddSizer(availSizer, 1, wx.EXPAND | wx.TOP, 6)
        label.SetSizer(labelAreaSizer)
        label.textCtrl = textSizer.textCtrl
                    
        #control
        control = wx.Panel(window)
        sizer = wx.BoxSizer(orient = wx.VERTICAL)
        self.sizer = sizer
        #edit
        editSizer = wx.BoxSizer(orient = wx.HORIZONTAL)
        sizer.Add(editSizer,flag=wx.EXPAND)
        # list of components on object
        editList = ComponentList(parent=control, size=WX_BUTTON_SIZE)
        editList.SetToolTipString("Components attached to object")
        editList.SetPopupMinWidth(100)
        editSizer.Add(editList, 1)
        self.editList = editList
        # edit
        editButton = buttons.ThemedGenButton(control, label='Edit')
        editButton.SetInitialSize((50,self.editList.Size[1]))
        editButton.SetToolTipString("Edit this component in a new window")
        editButton.Bind(wx.EVT_BUTTON, self.edit_button_click)
        self.editButton = editButton
        editSizer.Add(editButton, 0, wx.EAST, 5)
        #delete
        bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, 
                                       wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
        removeButton = buttons.ThemedGenBitmapButton(control, 
                                            size=WX_BUTTON_SIZE, bitmap=bmp)
        removeButton.SetToolTipString("Remove this component from object")
        removeButton.Bind(wx.EVT_BUTTON, self.remove_button_click)
        editSizer.Add( removeButton,0)
        
        #add
        addSizer = wx.BoxSizer(orient = wx.HORIZONTAL)
        sizer.Add(addSizer, flag=wx.EXPAND)
        # tree of available components
        addTree = ComponentAddTree(parent=control)
        addTree.SetPopupMinWidth(150)
        addTree.SetToolTipString("Component to add")
        addSizer.Add( addTree, 1)
        self.addTree = addTree
        # add button
        addButton = buttons.ThemedGenButton(control, 
                                            label='Add', style=wx.BU_EXACTFIT)
        addButton.SetInitialSize(editButton.Size) 
        addButton.SetToolTipString("Add selected component")
        addButton.Bind(wx.EVT_BUTTON, self.add_button_click)
        addSizer.Add( addButton, 0, wx.EAST, 5)
        
        # browse button
        bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK, 
                                       wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
        browseButton = buttons.ThemedGenBitmapButton(control, 
                                            size=WX_BUTTON_SIZE, bitmap=bmp)
        browseButton.SetToolTipString("Browse available components")
        addSizer.Add( browseButton,0)
        browseButton.Bind(wx.EVT_BUTTON, self.open_browser)
            # won't let me size normally!?
        
        #growertest
#        pane = control
#        button = wx.Button(pane, label='fakeass')
#        button.Bind(wx.EVT_BUTTON, self.expander_click)
#        button2 = wx.Button(pane, label='hider')
#        self.subButton = button2
#        sizer.AddMany( [(button), (button2)])
#        self.expanded = True

        control.SetSizer(sizer)
        control.SetMinSize((-1, -1))  
        sizer.SetMinSize((-1,-1))        
        sizer.Fit(control)
        addTree.SetMinSize((1,self.addTree.Size[1]))
        editList.SetMinSize((1,self.editList.Size[1]))
        
        aguidata.setdefault('doc', "")
        kwargs['aguidata'] = aguidata
        kwargs['label_widget'] = label
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, **kwargs)
        
        # keep the pug function around for button pressing
        # don't know if this is the right way to do it
        from pug.syswx.pugframe import PugFrame
        self.pug = PugFrame
                
    def expander_click(self, event=None):
        self.expanded = not self.expanded
#        self.subButton.Show(self.expanded)
        self.sizer.Layout()
        self.sizer.Fit(self.control)
        self.match_control_size()
        
    def setup(self, attribute, window, aguidata):
        for child in self.control.GetChildren():
            if isinstance(child, wx.TopLevelWindow):
                wx.CallAfter( child.Close)
#        aguidata.setdefault('background_color', self.defaultBackgroundColor)
        aguidata.setdefault('label','   components')
        try:
            resetObject = self.object != window.object
        except:
            resetObject = True
        if resetObject:
            self.object = window.object
            self.addTree.object = self.object
            self.editList.object = self.object
        try:
            selectComponent = self.editList.get_selected()
        except:
            selectComponent = None
        try:
            selectAddComponent = self.addTree.tree.GetStringValue()
        except:
            selectAddComponent = ""
        self.editList.refresh_components( selectComponent)
        self.addTree.create_tree( self.object)
        self.addTree.tree.SetStringValue( selectAddComponent)
        Base.setup(self, attribute, window, aguidata)
        
    def add_button_click(self, event=None):
        component = self.addTree.get_selected()
        if not component:
            retDlg = wx.MessageDialog(self.control, 
                    'First, use lower dropdown to select a component to add.', 
                    'No Component', wx.OK)
            retDlg.ShowModal() 
            self.applying = False
            retDlg.Destroy()                 
            return
        instance = self.object.components.add(component)
        self.editList.component_added(instance)
        self.window.refresh()
        
    def remove_button_click(self, event=None):
        component = self.editList.get_selected()
        if not component:
            return
        self.object.components.remove(component)
        self.editList.component_removed()
        wx.CallAfter(gc.collect)
        self.window.refresh()

    def edit_button_click(self, event=None):
        try:
            component = self.editList.get_selected()
        except:
            return
        if not component:
            return
        path = self.window.objectPath
        if not path:
            path = self.window.GetTitle()
        obj = component
        app = wx.GetApp()
        objectpath = ''.join([self.editList.get_text(), ' component of ', path])
        if wx.GetKeyState(wx.WXK_CONTROL) or not app.show_object_pugframe(obj):
            frame = self.pug(obj=obj, parent=None, 
                             objectpath=objectpath, show=False)
            self_rect = self.control.GetTopLevelParent().GetScreenRect()
            frame_rect = frame.GetScreenRect()
            display_size = wx.GetDisplaySize()
            if self_rect.Right + frame_rect.Width < display_size[0]:
                x = self_rect.Right
            elif self_rect.Left - frame_rect.Width > 0:
                x = self_rect.Left - frame_rect.Width
            else:
                x = 0
            if self_rect.Top + frame_rect.Height < display_size[1]:
                y = self_rect.Top
            elif frame_rect.Height < display_size[1]:
                y = display_size[1] - frame_rect.Height
            else:
                y = 0
            frame.SetPosition((x,y))
            frame.Show()
        
    def open_browser(self, event=None):
        browser = ComponentBrowseDlg(self.control, self.object, 
                                     self.addTree.get_selected())
        response = browser.ShowModal()
        if response == wx.ID_OK and browser.component:
            self.addTree.CheckTree()
            item = self.addTree.tree.FindItemByData(browser.component)
            if item:
                self.addTree.SelectItem(item)
        browser.Destroy()
        
