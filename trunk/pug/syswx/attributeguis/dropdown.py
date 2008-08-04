"""Dropdown attribute gui"""

import wx
import wx.combo

from pug.syswx.list_ctrl_combo_popup import ListCtrlComboPopup
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

class Dropdown (Base):
    """Customizable dropdown attribute GUI
    
Dropdown(attribute, frame, list=[], readonly=True, generator=None, 
            callback=None, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'list': the list of options in the dropdown.  List items can be in the form
        of a tuple: ( itemtext, itemdata) or just an object which will be 
        converted into the tuple (itemtext, itemdata=object).  Itemtext will be
        item.__name__ if possible... otherwise str(object). When the user makes 
        a selection in the dropdown, the attribute will be set to itemdata 
    'allow_typing': if True, user can type their own items
    'list_generator': as an alternative to the static list, this callable will 
        be called when the dropdown is displayed.  It should return a list as 
        described in the 'list' entry above.
    'callback': this function will be called when an item is selected. It will
        be passed the itemtext and itemdata selected.

For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, frame, aguidata={}, **kwargs):
        style = wx.TE_PROCESS_ENTER
        if not aguidata.get('allow_typing', False):
            style |= wx.CB_READONLY
        control = wx.combo.ComboCtrl(parent=frame.get_control_window(),
                                     style=style)
        control.SetMinSize((-1,WX_STANDARD_HEIGHT))
        listctrl = ListCtrlComboPopup()
        self.listctrl = listctrl
        control.SetPopupControl(listctrl)
        listctrl.SetSelectCallback(self.item_selected)
        control.Bind(wx.EVT_TEXT_ENTER, self.item_selected)
        
        self.callback = aguidata.get('callback',  None)
        self.list_generator = aguidata.get('list_generator', None)
        if self.list_generator:
            listctrl.SetPopupCallback(self.setup_listctrl)
        list = aguidata.get('list',[])
        self.setup_listctrl(list)

        kwargs['control_widget'] = control
        Base.__init__(self, attribute, frame, aguidata, **kwargs)
        
    def setup_listctrl(self, list=None):
        if not list and not callable(self.list_generator):
            return
        selectedData = self.listctrl.GetSelectedData()
        list = self.list_generator()
        self.listctrl.DeleteAllItems()
        for item in list:
            if isinstance(item, tuple):
                self.listctrl.AddItem( item[0], item[1])
            else:
                if hasattr(item,'__name__'):
                    name = item.__name__
                else:
                    name = str(item)
                self.listctrl.AddItem( name, item)
        i = self.listctrl.FindData(selectedData)
        if i:
            self.listctrl.SelectItem(i)
        self.data = self.listctrl.GetSelectedData()
        
        
    def item_selected(self, event=None):
        self.data = self.listctrl.GetSelectedData()
        self.apply()
        if self.callback:
            self.callback(self.listctrl.GetStringValue(), 
                          self.listctrl.GetSelectedData())
        if not self.tooltip:
            self.doc_to_tooltip()
        
    def get_control_value(self):
        return self.data
    
    def set_control_value(self, value):
        i = self.listctrl.FindData( value)
        if i == -1:
            # first, let's try refreshing the list if it's dynamic...
            if self.list_generator:
                self.setup_listctrl()
                i = self.listctrl.FindData(value)
            if i == -1:
            # if we still have a value that's not in the list, we want it to 
            # appear in the list anyway...
                i = self.listctrl.AddItem( str(value), value)
        self.listctrl.SelectItem(i)
        self.control.SetText(self.listctrl.GetStringValue()) 
        self.data = value
#        self.control.SetToolTipString( str(value))
        