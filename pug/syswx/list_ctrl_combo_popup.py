import wx
import wx.combo
wx=wx

"""This class is a popup containing a ListCtrl."""

class ListCtrlComboPopup(wx.ListBox, wx.combo.ComboPopup):
    """Popup control containing a list. Created because the built-in combo-box
doesn't have as many features/accessors as the combo.ComboCtrl"""

    def __init__(self):
        self.PostCreate(wx.PreListBox())
        wx.combo.ComboPopup.__init__(self)
        self.typedText = ''
        self.didSelect = True
        self.minWidth = 0
        self.maxHeight = 130
        
    def SetMinWidth(self, min):
        self.minWidth = min
        
    def SetMaxHeight(self, max):
        self.maxHeight = max    
        
    def Create(self, parent):
        wx.ListBox.Create(self, parent, style=wx.LB_SINGLE)
        self.list = self
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseSelect)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.LeaveWindow)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.selected = -1
        self.selectCallback = None
        self.popupCallback = None
        self.last_prefix = None
        
    def FindPrefix(self, prefix):
        if prefix:
            prefix = prefix.lower()
            if prefix == self.last_prefix:
                search = range(self.selected+1, self.GetCount()) + \
                        range(self.selected)
            else:
                search = range(self.GetCount())
            self.last_prefix = prefix
            # create a range that starts at currently selected+1, goes to end,
            # then loops to start
            for item in search:
                # lower case version of first character
                text = self.GetString(item)[0].lower()
                if text == prefix:
                    return item
        return -1

    def OnKey(self, evt):
        key = evt.GetKeyCode()
        if key >= 32 and key <= 127:
            item = self.FindPrefix(chr(key))
            if item != -1:
                self.SelectItem(item)
        elif key == wx.WXK_BACK or key == wx.WXK_LEFT:
            # backspace removes one character and backs up
            if not self.typedText:
                return
            self.typedText = self.typedText[:-1]
            item = self.FindPrefix(self.typedText)
            if item != -1:
                self.SetSelection(item)
        elif key == wx.WXK_UP:
            item = self.GetSelection()
            if item > 0:
                self.SetSelection(item-1)
        elif key == wx.WXK_DOWN:
            item = self.GetSelection()
            try:
                self.SetSelection(item+1)
            except:
                pass
        elif key == wx.WXK_ESCAPE or key == wx.WXK_TAB:
            self.Dismiss()
        elif key == wx.WXK_RETURN:
            self.OnSelect(None, self.GetSelection())
            self.GetCombo().SetValue(self.GetStringValue())
        else:
            evt.Skip()
        
    def AddItem(self, text, data=None):
        item = self.Append(text)
        self.SetClientData(item, data)
        return item

    def OnMotion(self, event):
        # have the selection follow the mouse, like in a real combobox
        selected = self.list.HitTest(event.GetPosition())
        if selected == -1:
            self.selected = -1
            self.list.Select(-1)
        elif selected != self.selected:
            self.selected = selected
            self.list.Select(selected)
        event.Skip()

    def LeaveWindow(self, event):
        self.list.DeselectAll()
        event.Skip()
        
    def GetControl(self):
        return self.list
    
    def GetSelectedData(self):
        if self.selected != -1:
            try:
                return self.list.GetClientData(self.selected)
            except:
                self.selected = -1
        return None
    
    def OnSelect(self, event=None, selected=-1):
        self.Dismiss()
        if selected == -1:
            self.SelectItem(self.originalSelection)
        self.selected = selected
        self.didSelect = True
        if event:
            event.Skip()
        if self.selectCallback:
            self.selectCallback(event)
    
    def OnPopup(self):
        self.didSelect = False
        self.originalSelection = self.GetSelection()
        if self.popupCallback:
            self.popupCallback(self)
        if self.selected:
            self.list.EnsureVisible(self.selected)
        
    def OnDismiss(self):
        try:
            self.GetCombo().OnDismissPopup()
        except:
            pass
        if not self.didSelect:
            try:
                self.SelectItem(self.originalSelection)
            except:
                pass
    
    def SetPopupCallback(self, callback):
        """SetPopupCallback( callback)

The callback will be called just before the popup control is popped up. It will
be called with one argument, which is this control, i.e. 
callback(self)
"""
        if not callable(callback) and callback is not None:
            raise ValueError(''.join([str(callback)," not callable"]))
        self.popupCallback = callback  
        
    def DeleteAllItems(self):
        self.list.Clear()
        
    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return wx.Size(self.minWidth or minWidth, min(self.maxHeight,maxHeight))
    
    def OnEnter(self, event):
        selected = self.list.GetSelection()
        self.OnSelect( event, selected)

    def OnMouseSelect(self, event):
        selected = self.list.HitTest(event.GetPosition())
        if selected == -1:
            selected = self.originalSelection
        self.OnSelect(event, selected)    
        
    def SetSelectCallback(self, callback):
        """SetSelectCallback( callback)

The callback will be called just after a selection is made.
"""        
        if not callable(callback):
            raise ''.join([str(callback)," not callable"])
        self.selectCallback = callback  
        
    def GetStringValue(self):
        if self.selected != -1:
            try:
                return self.list.GetString(self.selected)
            except:
                return ""   
        else:
            return ""
        
    def SelectItem(self, index):
        self.selected = index
        self.list.Select(index)
        
    def FindData(self, data):
        """FindData(data): find the first item with the given associated data"""
        c = self.list.GetCount()
        for i in range(c):
            itemdata = self.list.GetClientData(i)
            if itemdata == data:
                return i
        return -1
    
    def FindText(self, text):
        c = self.list.GetCount()
        for i in range(c):
            itemtext = self.list.GetString(i)
            if itemtext == text:
                return i
        return -1

