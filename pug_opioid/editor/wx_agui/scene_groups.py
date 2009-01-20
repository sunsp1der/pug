"""SceneGroups attribute gui... a list of groups with controls on right"""

import wx
import wx.lib.buttons as buttons

from pug.syswx.helpframe import HelpFrame
from pug.syswx.attributeguis import Base
from pug.syswx.wxconstants import WX_STANDARD_HEIGHT, WX_BUTTON_BMP_SIZE

class SceneGroups (Base):
    """An attribute gui that shows a list of groups and has control buttons

Group(attribute, window, aguidata, **kwargs)
aguidata: possible entries-
    'height': listbox height in pixels. Default = WX_STANDARD_HEIGHT * 3
attribute: what attribute of window.object is being controlled
window: the parent window. 
For other kwargs arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata, **kwargs):
        # control
        control = wx.Panel(parent=window)
        height = aguidata.get('height', WX_STANDARD_HEIGHT * 3)
        control.MinSize = (-1, height+2)
        sizer = wx.GridBagSizer()
        control.SetSizer(sizer)
        self.list = []
        listbox = wx.ListBox(control, -1)
        listbox.MaxSize = (-1, height)
        listbox.MinSize = (-1, height)
        self.listbox = listbox
        
        #add button
        add = buttons.ThemedGenBitmapButton(control, -1, None,
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT))
        bmp = wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, 
                                       wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
        add.SetBitmapLabel(bmp)       
        add.SetToolTipString("Add a group")
        add.Bind(wx.EVT_BUTTON, self.evt_add_button)
        #delete button
        delete = buttons.ThemedGenBitmapButton(control, -1, None,
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT))
        bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, 
                                       wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
        delete.SetBitmapLabel(bmp)       
        delete.SetToolTipString("Delete selected group")
        delete.Bind(wx.EVT_BUTTON, self.evt_delete_button)
        #info button
#        info = buttons.ThemedGenBitmapButton(control, -1, None,
#                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT))
#        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, 
#                                       wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
#        info.SetBitmapLabel(bmp)
#        info.SetToolTipString("Info about using Opioid2D groups")
#        info.Bind(wx.EVT_BUTTON, self.evt_info_button)
        line = wx.StaticLine(control,pos=(0,0))
        line.MaxSize = (-1,1)
        sizer.Add(line,(3,0),flag=wx.EXPAND)
        sizer.Add(listbox, (0, 0),(3, 1), flag=wx.EXPAND | wx.EAST, border = 4)
        sizer.Add(delete, (0, 1))
        sizer.Add(add, (1, 1))
        sizer.Add(info, (2, 1))
        sizer.AddGrowableCol(0)
        #sizer.AddGrowableRow(3)
        
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)     
        
    def evt_add_button(self, event=None):
        dlg = wx.TextEntryDialog( self.control, 
                                  "Enter the new group's name", 
                                  "New Group")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            name.strip()
            if name:
                self.window.object.add_group(str(name))
                self.refresh()
        dlg.Destroy()

    def evt_delete_button(self, event=None):
        dlg = wx.MessageDialog(self.control,
                    '\n'.join(['Deleting group will delete all',
                               'nodes on the group. Continue?']),
                           'Confirm Delete', wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_YES:
            group = self.listbox.GetStringSelection()
            if group:
                self.window.object.delete_group(str(group))
            self.refresh()
        dlg.Destroy()

    def evt_info_button(self, event=None):
        group = self.listbox.GetStringSelection()
        if group:
            object = self.window.object.get_group(str(group))
            showButton = True
        else:
            object = None
            showButton = False
        text = '\n'.join(
                ["Scene groups\n",
                 "To rearrange the order of groups, you must edit the",
                 "groups attribute in this scene's file."])
        frame = HelpFrame( object, self.control, 
                objectPath=''.join([self.window.objectPath, '.groups']),
                showPugButton=showButton, showRetypeButton=False, text=text)
        frame.Show()
        frame.Center()
        
    def get_control_value(self):
        return self.list
    
    def set_control_value(self, value):
        self.list = value
        value.reverse()
        self.listbox.Set(value)
        