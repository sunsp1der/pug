"""ListEdit attribute gui"""

import wx
import wx.lib.buttons as buttons

from pug.util import get_image_path
from pug.syswx.helpframe import HelpFrame
from pug.syswx.attributeguis import Base
from pug.syswx.wxconstants import WX_STANDARD_HEIGHT, WX_BUTTON_BMP_SIZE

class ListEdit (Base):
    """Customizable listbox attribute GUI for controlling lists
    
ListEdit(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'list': the list of options in the dropdown.  List items can be in the form
        of a tuple: ( itemtext, itemdata) or just an object which will be 
        converted into the tuple (itemtext, itemdata=object).  Itemtext will be
        item.__name__ if possible... otherwise str(object). When the user makes 
        a selection in the dropdown, the attribute will be set to itemdata 
    'list_generator': as an alternative to the static list, this callable will 
        be called when the listbox refreshes the list.  It should return a list 
        as described in the 'list' entry above.
    'height': the height of the listbox
    'reverse': reverse the order of list items when displayed
    The following define buttons to be used. If the item is not in the aguidata
        list, the button will not be shown. Methods will be called as 
        fn(agui, wxevent). Use agui.listbox to access listbox control and 
        agui.list to access the list itself. 
    'add':[add method, add tooltip] default method brings up a text entry
        dialog for item. Item will be added before currently selected item.
        Default tooltip: "Add an item"
    'delete':[delete method, delete tooltip] default method deletes currently
        selected item, default tooltip: "Delete selected item"
    'info':[info text, info tooltip]: Info text is not optional... this string 
        will be displayed in a help window. default tooltip: "Info about this 
        list"

For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        #control
        control = wx.Panel(parent=window)
        sizer = wx.GridBagSizer()
        control.SetSizer(sizer)
        self.list = []
        #generate list
        self.list_generator = aguidata.get('list_generator', None)
        add = delete = info = arrange_up = arrange_down = None
        #add button
        if aguidata.get('add', False):
            addinfo = aguidata['add']
            if len(addinfo) > 0:
                addfn = addinfo[0]
            else:
                addfn = self.evt_add_button
            if len(addinfo) > 1:
                tooltip = addinfo[1]
            else:
                tooltip = "Add an item"
            add = wx.BitmapButton(control, -1, 
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT))
            add_image = wx.Bitmap(get_image_path("add.png"), wx.BITMAP_TYPE_PNG)
            add.SetBitmapLabel(add_image)       
            add.SetToolTipString(tooltip)
            add.Bind(wx.EVT_BUTTON, addfn)
        #delete button
        if aguidata.get('delete', False):
            deleteinfo = aguidata['delete']
            if len(deleteinfo) > 0:
                deletefn = deleteinfo[0]
            else:
                deletefn = self.evt_delete_button
            if len(deleteinfo) > 1:
                tooltip = deleteinfo[1]
            else:
                tooltip = "Delete an item"
            delete = wx.BitmapButton(control, -1, 
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT))
            remove_image = wx.Bitmap(get_image_path("delete.png"), 
                                     wx.BITMAP_TYPE_PNG)
            delete.SetBitmapLabel(remove_image)       
            delete.SetToolTipString(tooltip)
            delete.Bind(wx.EVT_BUTTON, deletefn)
        #info button
        if aguidata.get('info', False):
            infoinfo = aguidata['info']
            self.infotext = infoinfo[0]
            if len(infoinfo) > 1:
                tooltip = infoinfo[1]
            else:
                tooltip = "Info about this list"        
            info = wx.BitmapButton(control, -1,
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT))
            bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, 
                                           wx.ART_TOOLBAR, WX_BUTTON_BMP_SIZE)
            info.SetBitmapLabel(bmp)
            info.SetToolTipString(tooltip)
            info.Bind(wx.EVT_BUTTON, self.evt_info_button)
            
        #arrange buttons
        if aguidata.get('arrange_up', False):
            arrange_upinfo = aguidata['arrange_up']
            if len(arrange_upinfo) > 0:
                arrange_upfn = arrange_upinfo[0]
            else:
                arrange_upfn = self.evt_arrange_up_button
            if len(arrange_upinfo) > 1:
                tooltip = arrange_upinfo[1]
            else:
                tooltip = "Move selected item up"
            arrange_up = wx.BitmapButton(control, -1, 
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT/2))
            arrange_up_image = wx.Bitmap(get_image_path("arrow_up.png"), 
                                     wx.BITMAP_TYPE_PNG)
            arrange_up.SetBitmapLabel(arrange_up_image)       
            arrange_up.SetToolTipString(tooltip)
            arrange_up.Bind(wx.EVT_BUTTON, arrange_upfn)
        if aguidata.get('arrange_down', False):
            arrange_downinfo = aguidata['arrange_down']
            if len(arrange_downinfo) > 0:
                arrange_downfn = arrange_downinfo[0]
            else:
                arrange_downfn = self.evt_arrange_down_button
            if len(arrange_downinfo) > 1:
                tooltip = arrange_downinfo[1]
            else:
                tooltip = "Move selected item down"
            arrange_down = wx.BitmapButton(control, -1, 
                                size=(WX_STANDARD_HEIGHT, WX_STANDARD_HEIGHT/2))
            arrange_down_image = wx.Bitmap(get_image_path("arrow_down.png"), 
                                     wx.BITMAP_TYPE_PNG)
            arrange_down.SetBitmapLabel(arrange_down_image)       
            arrange_down.SetToolTipString(tooltip)
            arrange_down.Bind(wx.EVT_BUTTON, arrange_downfn)
        line = wx.StaticLine(control,pos=(0,0))
        line.MaxSize = (-1,1)
        buttons = 0
        defaultsize = 0
        for button in [delete, add, info, arrange_up, arrange_down]:
            if button:
                sizer.Add(button, (buttons,1))
                defaultsize += button.GetSize()[1]
                buttons+=1
        height = aguidata.get('height', defaultsize)
        control.MinSize = (-1, height+2)
        listbox = wx.ListBox(control, -1)
        listbox.MaxSize = (-1, height)
        listbox.MinSize = (-1, height)
        self.listbox = listbox
        sizer.Add(line,(buttons,0),flag=wx.EXPAND)
        sizer.Add(listbox, (0, 0),(buttons, 1), flag=wx.EXPAND | wx.EAST, 
                  border = 4)
        sizer.AddGrowableCol(0)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def setup(self, attribute, window, aguidata):
        if self.aguidata != aguidata:
            self.control.Destroy()
            self.label.Destroy()            
            self.__init__(attribute, window, aguidata)
            return
        else:
            Base.setup( self, attribute, window, aguidata)
        
    def evt_add_button(self, event=None):
        #TODO:  put in default behavior
        self.refresh()

    def evt_delete_button(self, event=None):
        #TODO:  put in default behavior
        self.refresh()
        
    def evt_arrange_up_button(self, event=None):
        #TODO: put in default behavior
        self.refresh()

    def evt_arrange_down_button(self, event=None):
        #TODO: put in default behavior
        self.refresh()

    def evt_info_button(self, event=None):
        frame = HelpFrame( None, self.control, 
                objectPath=''.join([self.window.objectPath, '.', 
                                    self.label.textCtrl.LabelText.strip()]),
                showPugButton=False, showRetypeButton=False, text=self.infotext)
        frame.Show()
        frame.Center()        
        
    def setup_listctrl(self, list=None):
        if callable(self.list_generator):
            list = self.list_generator()
        elif list is None:
                return
        idx = self.listbox.GetSelection()
        if idx != -1:
            selected = self.listbox.GetClientData(idx)
        else:
            selected = None
        self.listbox.Clear()
        self.datalist = []
        self.list = []
        for item in list:
            if isinstance(item, tuple):
                name = item[0]
                data = item[1]
            else:
                data = item
                if hasattr(item,'__name__'):
                    name = item.__name__
                else:
                    name = str(item)
            idx = self.listbox.Append( name, item)
            if selected and item == selected:
                self.listbox.Select(idx)
            self.datalist.append([name, data])
            self.list.append(name)
               
    def get_control_value(self):
        return self.list
    
    def set_control_value(self, value):
        if self.aguidata.get('reverse_list', False):
            value.reverse()
        self.setup_listctrl( value)