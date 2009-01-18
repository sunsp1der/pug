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
        self.list=wx.ListBox(parent, style=wx.LB_SINGLE)
#        self.list = FindPrefixListBox(parent, style = wx.LB_SINGLE)
        self.list.Bind(wx.EVT_MOTION, self.OnMotion)
        self.list.Bind(wx.EVT_LEFT_DOWN, self.OnMouseSelect)
        
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
        if not callable(callback) and callback is not None:
            raise ValueError(''.join([str(callback)," not callable"]))
        self.popupCallback = callback  
    
    def AddItem(self, text, data=None):
        item = self.list.Append(text)
        self.list.SetClientData(item, data)
        return item
        
    def DeleteAllItems(self):
        self.list.Clear()
        
    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return wx.Size(minWidth, min(200,maxHeight))
    
    def OnEnter(self, event):
        selected = self.list.GetSelection()
        self.OnSelect( event, selected)

    def OnSelect(self, event, selected):
        if selected != -1:
            self.selected = selected
        
        self.Dismiss()
        event.Skip()
        if self.selectCallback:
            self.selectCallback(event)        
    
    def OnMouseSelect(self, event):
        selected = self.list.HitTest(event.GetPosition())
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
    
#---------------------------------------------------------------------------

# This listbox subclass lets you type the starting letters of what you want to
# select, and scrolls the list to the match if it is found.
class FindPrefixListBox(wx.ListBox):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, choices=[], style=0, 
                 validator=wx.DefaultValidator):
        wx.ListBox.__init__(self, parent, id, pos, size, choices, style, validator)
        self.typedText = ''
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)


    def FindPrefix(self, prefix):
        if prefix:
            prefix = prefix.lower()
            length = len(prefix)

            # Changed in 2.5 because ListBox.Number() is no longer supported.
            # ListBox.GetCount() is now the appropriate way to go.
            for x in range(self.GetCount()):
                text = self.GetString(x)
                text = text.lower()

                if text[:length] == prefix:
                    return x

        return -1


    def OnKey(self, evt):
        key = evt.GetKeyCode()
        if key >= 32 and key <= 127:
            self.typedText = self.typedText + chr(key)
            item = self.FindPrefix(self.typedText)

            if item != -1:
                self.SetSelection(item)

        elif key == wx.WXK_BACK:   # backspace removes one character and backs up
            self.typedText = self.typedText[:-1]

            if not self.typedText:
                self.SetSelection(0)
            else:
                item = self.FindPrefix(self.typedText)

                if item != -1:
                    self.SetSelection(item)
        else:
            self.typedText = ''
            evt.Skip()

    def OnKeyDown(self, evt):
        pass
   
