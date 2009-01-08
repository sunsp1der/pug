"""Simple text entry attribute gui"""

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
    """Label attribute GUI for demarking GUI sections. Not for attributes
    
Label(attribute, window, aguidata, **kwargs)
attribute: this value is ignored
window: the parent pugFrame
aguidata: {'label':<text to use>,
    'font_size':<int>, 
    'background_color': wxColor, colorIDString, Hex number, or int tuple
    'indent': number of pixels to indent the label
    }
aguidata values default to the standard text look with a slightly 
darkened background...
    
# TODO:
#    'font_color': wxColor, colorIDString, Hex number, or int tuple,
#    'font_weight': wx.FONTWEIGHT_xxx constant,
#    'font_underline': bool,
#    'font_family': 
# TODO: examine some nicer ways to make fonts... FFont etc
For kwargs optional arguments, see the Base attribute GUI
"""
    expanded = False
    def __init__(self, attribute, frame, aguidata={}, **kwargs):
        #label
        label = wx.Panel(frame.get_label_window(), style=0)        
        if not aguidata.has_key('background_color'):
            backgroundColor = label.GetBackgroundColour()
            r = backgroundColor[0] - 10
            g = backgroundColor[1] - 10
            b = backgroundColor[2] - 10
            if r < 0: r = 0
            if g < 0: g = 0
            if b < 0: b = 0
            backgroundColor.Set(r,g,b)
            aguidata['background_color']=backgroundColor
        if aguidata.has_key('label'):
            labelText = aguidata['label']
        else:
            labelText = '   components'
        textSizer = AguiLabelSizer(parent=label, label=labelText, line=True)
        text = textSizer.text
        # label.preferredWidth = textSizer.preferredWidth # FOR SASH
        label.SetSizer(textSizer)
        self.object = None
                    
        #control
        control = wx.Panel(frame.get_control_window())
        sizer = wx.BoxSizer(orient = wx.VERTICAL)
        self.sizer = sizer
        #edit
        editSizer = wx.BoxSizer(orient = wx.HORIZONTAL)
        sizer.Add(editSizer,flag=wx.EXPAND)
        # combo
        editList = ComponentList(parent=control, size=WX_BUTTON_SIZE)
        editList.SetToolTipString("Components attached to object")
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
        # tree
        addTree = ComponentAddTree(parent=control)
        addTree.SetPopupMinWidth(100)
        addTree.SetToolTipString("Component to add to object")
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
        addTree.SetMinSize((-1,self.addTree.Size[1]))
        editList.SetMinSize((-1,self.editList.Size[1]))
        
        kwargs['aguidata'] = aguidata
        kwargs['label_widget'] = label
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, frame, **kwargs)
        
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
        
    def refresh(self):
        if self.object != self._window.object:
            self.object = self._window.object
            self.addTree.object = self.object
            self.editList.object = self.object
        Base.refresh(self)
        
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
        
    def remove_button_click(self, event=None):
        component = self.editList.get_selected()
        if not component:
            return
        self.object.components.remove(component)
        self.editList.component_removed()

    def edit_button_click(self, event=None):
        component = self.editList.get_selected()
        if not component:
            return
        path = self._window.objectPath
        if not path:
            path = self._window.GetTitle()
        obj=component
        app = wx.GetApp()
        if not app.show_object_pugframe(obj) or wx.GetKeyState(wx.WXK_CONTROL):
            frame = self.pug(obj=obj, parent=self.control, objectpath=''.join(
                        [self.editList.get_text(), ' component of ', path]))
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
        
