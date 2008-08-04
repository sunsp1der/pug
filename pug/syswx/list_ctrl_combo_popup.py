import wx
import wx.combo

"""This class is a popup containing a ListCtrl."""

class ListCtrlComboPopup(wx.combo.ComboPopup):
    """Popup control containing a list. Created because the built-in combo-box
doesn't have as many features/accessors as the combo.ComboCtrl"""
    selected = -1      
    selectCallback = None  
    popupCallback = None
        
    def Create(self, parent):
        self.list = wx.ListBox(parent, style = wx.LB_SINGLE)
        self.list.Bind(wx.EVT_MOTION, self.OnMotion)
        self.list.Bind(wx.EVT_LEFT_DOWN, self.OnSelect)
        
    def DeselectAll(self):
        return self.list.DeselectAll()
        
    def GetControl(self):
        return self.list
    
    def GetSelectedData(self):
        selection = self.list.GetSelection()
        if selection != wx.NOT_FOUND:
            return self.list.GetClientData(selection)
        else:
            return None
    
    def OnPopup(self):
        if self.popupCallback:
            self.popupCallback(self)
        if self.selected:
            self.list.EnsureVisible(self.selected)
    
    def SetPopupCallback(self, callback):
        """SetPopupCallback( callback)

The callback will be called just before the popup control is popped up. It will
be called with one argument, which is this control, i.e. 
callback(self)
"""
        if not callable(callback):
            raise ''.join([str(callback)," not callable"])
        self.popupCallback = callback  
    
    def AddItem(self, text, data=None):
        item = self.list.Append(text)
        self.list.SetClientData(item, data)
        return item
        
    def DeleteAllItems(self):
        self.list.Clear()
        
    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return wx.Size(minWidth, min(200,maxHeight))
    
    def OnSelect(self, event):
        selected = self.list.HitTest(event.GetPosition())
        if selected != -1:
            self.selected = selected
        self.Dismiss()
        event.Skip()    
        if self.selectCallback:
            self.selectCallback( event)    
        
    def SetSelectCallback(self, callback):
        """SetSelectCallback( callback)

The callback will be called just after a selection is made.
"""        
        if not callable(callback):
            raise ''.join([str(callback)," not callable"])
        self.selectCallback = callback  
        
    def GetStringValue(self):
        if self.selected != -1:
            return self.list.GetString(self.selected)   
        else:
            return ""

    def OnMotion(self, event):
        # have the selection follow the mouse, like in a real combobox
        selected = self.list.HitTest(event.GetPosition())
        if selected != -1 and selected != self.selected:
            self.selected = selected
            self.list.Select(selected)
        event.Skip()
        
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
