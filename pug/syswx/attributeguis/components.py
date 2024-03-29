"""components.py - component viewer attribute gui"""

from functools import partial

import wx
import wx.lib.buttons as buttons
wx=wx

from pug.util import get_image_path
from pug.syswx.wxconstants import *
from pug.syswx.pugbutton import PugButton
from pug.syswx.agui_label_sizer import AguiLabelSizer
from pug.syswx.component_helpers import ComponentAddTree, ComponentList
from pug.syswx.attributeguis.base import Base
from pug.syswx.component_browser import ComponentAddDlg
from pug.syswx.util import show_exception_dialog, close_obj_windows

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
        editSizer.Add(editList, 1, wx.EXPAND, 5)
        self.editList = editList
        # edit button
        edit_image = wx.Bitmap(get_image_path("edit.png"), wx.BITMAP_TYPE_PNG)
        editButton = wx.BitmapButton(control, size=WX_BUTTON_SIZE,
                                                   bitmap=edit_image)
#        editButton.SetInitialSize((50,self.editList.Size[1]))
        editButton.SetToolTipString("Edit this component in a new window")
        editButton.Bind(wx.EVT_BUTTON, self.edit_button_click)
        self.editButton = editButton
        editSizer.Add(editButton, 0, wx.EAST)
        #delete
        remove_image = wx.Bitmap(get_image_path("delete.png"), 
                                 wx.BITMAP_TYPE_PNG)
        removeButton = wx.BitmapButton(control, 
                                    size=WX_BUTTON_SIZE, bitmap=remove_image)
        removeButton.SetToolTipString("Remove this component from object")
        removeButton.Bind(wx.EVT_BUTTON, self.remove_button_click)
        editSizer.Add( removeButton,0, wx.EXPAND, 5)
        
        # add button
        add_image = wx.Bitmap(get_image_path("add.png"), wx.BITMAP_TYPE_PNG)
        
        addButton = wx.BitmapButton(control, 
                                    size=WX_BUTTON_SIZE, bitmap=add_image)
#        addButton.SetInitialSize(editButton.Size) 
        addButton.SetToolTipString("Pick a component to add to this object")
        addButton.Bind(wx.EVT_BUTTON, self.add_button_click)
        editSizer.Add( addButton, 0, wx.EAST)
                
        control.SetSizer(sizer)
        control.SetMinSize((-1, -1))  
        sizer.SetMinSize((-1,-1))        
        sizer.Fit(control)
#        addTree.SetMinSize((1,self.addTree.Size[1]))
        editList.SetMinSize((1,self.editList.Size[1]))
        
        kwargs['aguidata'] = aguidata
#        kwargs['label_widget'] = label
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, **kwargs)
        
        # keep the pug function around for button pressing
        # don't know if this is the right way to do it
        from pug.syswx.pugframe import PugFrame
        self.pugframe = PugFrame
                
    def setup(self, attribute, window, aguidata):
        for child in self.control.GetChildren():
            if isinstance(child, wx.TopLevelWindow):
                wx.CallAfter( child.Close)
#        aguidata.setdefault('background_color', self.defaultBackgroundColor)
        aguidata.setdefault('doc', "")
        aguidata.setdefault('label','   components')
        try:
            resetObject = self.object != window.object
        except:
            resetObject = True
        if resetObject:
            self.object = window.object
#            self.addTree.object = self.object
            self.editList.object = self.object
        try:
            selectComponent = self.editList.get_selected()
        except:
            selectComponent = None
#        try:
#            selectAddComponent = self.addTree.tree.GetStringValue()
#        except:
#            selectAddComponent = ""
        self.editList.refresh_components( selectComponent)
#        self.addTree.create_tree( self.object)
#        self.addTree.tree.SetStringValue( selectAddComponent)
        Base.setup(self, attribute, window, aguidata)
        
    def add_button_click(self, event=None):
        dlg = ComponentAddDlg( None, self.object)
        #dlg.Center()
        if dlg.ShowModal() == wx.ID_OK:
            component = dlg.component
        else:
            component = None
        if component:
            try:
                dlg.browser.tree.AddRecent(component)
                instance = self.object.components.add(component)                
                do_fn = partial( self.object.components.add, instance)
                undo_fn = partial( remove_component, self.object, instance)
                if self.aguidata['undo']:
                    wx.GetApp().history.add(
                                        "Add component: " + component.__name__,
                                        undo_fn, do_fn)
                self.editList.component_added(instance)
                self.window.refresh()
                self.edit_button_click()
            except:
                show_exception_dialog()
        dlg.Destroy()
                
    def refresh(self, event=None):
        try:
            component = self.editList.get_selected()
            if component not in self.object.components.get():
                self.editList.component_removed()
        except:
            pass
                
    def remove_button_click(self, event=None):
        component = self.editList.get_selected()
        if not component:
            return
        do_fn = partial( remove_component, self.object, component)
        undo_fn = partial( self.object.components.add, component)
        do_fn()
        if self.aguidata['undo']:
            wx.GetApp().history.add(
                                "Delete component: " + self.editList.get_text(),    
                                undo_fn, do_fn)
        self.editList.component_removed()
        self.window.refresh()

    def edit_button_click(self, event=None):
        try:
            component = self.editList.get_selected()
        except:
            component = None
        if not component:
            retDlg = wx.MessageDialog(self.control, 
                    'No component selected to edit.', 
                    'No Component', wx.OK)
            retDlg.ShowModal() 
            retDlg.Destroy()                 
            return
        path = self.window.objectPath
        if not path:
            path = self.window.GetTitle()
        obj = component
        app = wx.GetApp()
        objectpath = ''.join([self.editList.get_text(), ' component of ', path])
        if wx.GetKeyState(wx.WXK_CONTROL) or not app.show_object_frame(obj):
            frame = self.pugframe(obj=obj, 
                                  parent=wx.GetApp().get_project_frame(), 
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
            self.window.refresh()
            frame.Show()
        
    def open_browser(self, event=None):
        browser = ComponentPickDlg(self.control, self.object, 
                                     self.addTree.get_selected())
        response = browser.ShowModal()
        if response == wx.ID_OK and browser.component:
            self.addTree.CheckTree()
            item = self.addTree.tree.FindItemByData(browser.component)
            if item:
                self.addTree.SelectItem(item)
        browser.Destroy()
        
def remove_component( object, component):
    object.components.remove(component)
    close_obj_windows(component)
