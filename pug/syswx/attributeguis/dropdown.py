"""Dropdown attribute gui"""

import wx
import wx.combo


from pug.syswx.list_ctrl_combo_popup import ListCtrlComboPopup
from pug.syswx.wxconstants import *
from pug.syswx.attributeguis.base import Base

_DEBUG = False

class Dropdown (Base):
    """Customizable dropdown attribute GUI
    
Dropdown(attribute, window, aguidata, **kwargs)

attribute: what attribute of window.object is being controlled
window: the parent pugFrame
aguidata: { 
    'list': the list of options in the dropdown.  List items can be in the form
        of a tuple: ( itemtext, itemdata) or just an object which will be 
        converted into the tuple (itemtext, itemdata=object).  Itemtext will be
        item.__name__ if possible... otherwise str(object). When the user makes 
        a selection in the dropdown, the attribute will be set to itemdata 
    'allow_typing': if True, user can type their own items. if the value typed
         is not in the list, itemdata will be set to itemtext. Default: False.
    'list_generator': as an alternative to the static list, this callable will 
        be called when the dropdown is displayed.  It should return a list as 
        described in the 'list' entry above.
    'callback': this function will be called when an item is selected, after the
        itemdata is applied to the attribute... callback( itemtext, itemdata)
    'dropdown_tooltip': show a tooltip for the currently selected item in the 
        dropdown

For kwargs optional arguments, see the Base attribute GUI
"""
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        style = wx.TE_PROCESS_ENTER
        if aguidata.get('allow_typing', False):
            self.allow_typing = True
        else:
            self.allow_typing = False
            style |= wx.CB_READONLY
        control = wx.combo.ComboCtrl(parent=window,
                                     style=style)
        if _DEBUG: print "DropDown.__init__ attribute:",attribute
        control.SetMinSize((1,WX_STANDARD_HEIGHT))
        listctrl = ListCtrlComboPopup()
        self.listctrl = listctrl
        control.SetPopupControl(self.listctrl)
        self.listctrl.SetSelectCallback(self.item_selected)
        control.Bind(wx.EVT_TEXT_ENTER, self.item_selected)
        control.Bind(wx.EVT_KILL_FOCUS, self.lost_focus)
        control.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)

    def apply(self, event=None):
        self.applying = True
        self.item_selected()
        self.applying = False
        Base.apply( self, event)
 
    def setup(self, attribute, window, aguidata):
        if self.allow_typing != aguidata.get('allow_typing', False):
            self.control.Destroy()
            self.label.Destroy()
            self.__init__( attribute, window, aguidata)
            return
        if _DEBUG: print "DropDown.setup attribute:",attribute
        self.callback = aguidata.get('callback',  None)
        self.list_generator = aguidata.get('list_generator', None)
        if self.list_generator:
            self.listctrl.SetPopupCallback(self.setup_listctrl)
        else:
            self.listctrl.SetPopupCallback(None)
        Base.setup(self, attribute, window, aguidata)
        self.setup_listctrl(self.aguidata.get('list',[]))
        self.set_control_value(self.get_attribute_value())

    def OnKey(self, ev):
        if ev.GetKeyCode() == wx.WXK_TAB:
            if ev.ShiftDown():
                self.control.Navigate(False)
            else:
                self.control.Navigate() 
            self.control.SetValue(self.control.GetValue())                
        else:
            ev.Skip()   
         
    def setup_listctrl(self, list=None):
        if not list and not callable(self.list_generator):
            return
        selectedData = self.listctrl.GetSelectedData()
        if self.list_generator:
            list = self.list_generator()
        self.listctrl.DeleteAllItems()
        namedict = {}
        for item in list:
            if isinstance(item, tuple):
                self.listctrl.AddItem( item[0], item[1])
            else:
                if hasattr(item,'__name__'):
                    name = item.__name__
                else:
                    name = str(item)
                namedict[name] = item
        namelist = namedict.keys()
        namelist.sort()
        for key in namelist:
            self.listctrl.AddItem( key, namedict[key])
        i = self.listctrl.FindData(selectedData)
        if i != -1:
            self.listctrl.SelectItem(i)
            self.data = self.listctrl.GetSelectedData()
        else:
            self.data = None
        self.set_tooltip()
        
    def lost_focus(self, event=None):
        if self.allow_typing and \
                self.listctrl.GetStringValue() != self.control.Value:
            self.data = self.control.Value
            self.text = self.control.Value
        elif not self.listctrl.didSelect:
            self.refresh()
            return
        Base.apply( self)
        if self.callback:
            self.callback(self.text, self.data)
        self.control.SetValue(self.control.GetValue())                            
        
    def item_selected(self, event=None):
        if self.allow_typing and \
                self.listctrl.GetStringValue() != self.control.Value:
            self.data = self.control.Value
            self.text = self.control.Value
        else:
            self.data = self.listctrl.GetSelectedData()
            self.text = self.listctrl.GetStringValue()
        if not self.applying: 
            Base.apply( self)
        if self.callback:
            self.callback(self.text, self.data)
        self.set_tooltip()
            
    def set_tooltip(self):
        if self.aguidata.get('dropdown_tooltip', False):
            if hasattr(self.data,'__doc__') and self.data.__doc__:
                self.control.SetToolTipString(self.data.__doc__)
                self.control.GetToolTip().Enable(True)
            else:
                self.control.SetToolTipString(' ')
                
    def get_control_value(self):
        return self.data
    
    def set_control_value(self, value):
        #  first try to match data
        i = self.listctrl.FindData( value)
        if i == -1:
#            # then, try to match text
#            i = self.listctrl.FindText( value)  
            if i == -1 and self.list_generator:
            # then, let's try refreshing the list if it's dynamic...
                self.setup_listctrl()
                i = self.listctrl.FindData(value)
                if i == -1:
#                    i = self.listctrl.FindText( value)  
#                    if i == -1:
            # if we still have a value that's not in the list, we want it to 
            # appear in the list anyway...
                    i = self.listctrl.AddItem( str(value), value)
        self.listctrl.SelectItem(i)
        self.control.SetText(self.listctrl.GetStringValue()) 
        self.data = value
        self.set_tooltip()
#        self.control.SetToolTipString( str(value))
        