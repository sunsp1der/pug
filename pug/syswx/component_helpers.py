"""Helper controls for components agui.

ComponentAddTree
ComponentList
TreeCtrlComboPopup
"""

from time import time
import weakref

import wx
import wx.combo


from pug.syswx.list_ctrl_combo_popup import ListCtrlComboPopup
from pug.component.manager import get_component_list, get_last_component_update
from pug.component.util import is_valid_component_class

class ComponentAddTree(wx.combo.ComboCtrl):
    """A dropdown tree of all available components for a given object"""
    allTreesNeedUpdate = 0
    def __init__(self, *args, **kwargs):
        kwargs['style']=wx.CB_READONLY
        wx.combo.ComboCtrl.__init__(self, *args, **kwargs)
        self.__object = None
        self.lastTreeUpdate = 0
#        self.SetButtonPosition(side=wx.WEST)
        popup = ComponentTreePopup()
        self.tree = popup
        self.SetPopupControl(popup)

    def SelectItem(self, item):
        self.tree.SelectItem(item)
        self.SetText( self.tree.GetStringValue())

    def CheckTree(self):
        if get_last_component_update() > self.lastTreeUpdate:
            self.allTreesNeedUpdate = get_last_component_update()
        
        if self.treesNeedUpdate or self.allTreesNeedUpdate > self.lastTreeUpdate:
            self.create_tree(self.__object)

            
    def get_object(self):
        return self.__object
    
    def set_object(self, object):
        self.set_tree_dirty()
        self.__object = object
        
    object = property(get_object,set_object)

    def create_tree(self, object):
        """create_tree(self,object)

object: the object that is being viewed.        
Build the popup tree control.  Call when object is changed or set.
"""
        wx.BeginBusyCursor()
        self.__object = object
        self.tree.tree.CreateComponentTree(object)
          
        self.treesNeedUpdate = False # this instance has been updated
        self.lastTreeUpdate = time() # for check against component manager
        wx.EndBusyCursor()
#        tree.SortAllItems()

    def OnButtonClick(self):
        """OnButtonClick - over-ride of ComboCtrl version"""
        self.CheckTree()
        wx.combo.ComboCtrl.OnButtonClick(self)
        
    
    def set_tree_dirty(self):
        """set_tree_dirty()
        
Recalculate tree next time it is shown. Can be called on ComponentTree class
to set all instances to recalculate next time tree is exposed.
"""
        if self is ComponentAddTree:
            # if called on class
            self.allTreesNeedUpdate = time.time()
        else:
            self.treesNeedUpdate = True
        
    def get_selected(self):
        return self.tree.GetSelectedData()

#===============================================================================
#
#===============================================================================

class ComponentList(wx.combo.ComboCtrl):
    def __init__(self, *args, **kwargs):
        kwargs['style']=wx.CB_READONLY
        wx.combo.ComboCtrl.__init__(self, *args, **kwargs)
        self.__object = None
        popup = ListCtrlComboPopup()
        self.listCtrl = popup
        self.SetPopupControl(popup)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)

    def OnKey(self, ev):
        if ev.GetKeyCode() == wx.WXK_TAB:
            if ev.ShiftDown():
                self.Navigate(False)
            else:
                self.Navigate() 
            self.SetValue(self.GetValue())
        else:
            ev.Skip()   

    def get_object(self):
        return self.__object
     
    def set_object(self, object):
        self.__object = object
        self.refresh_components()
        
        
    object = property(get_object,set_object)        

    def refresh_components(self, selectComponent=None):
        """refresh_components(selectComponent=None)->selected index

Refresh the list of components on the object. selectComponent allows you to 
choose a given component to be selected after refresh. 
"""
        retValue = None
        self.listCtrl.DeleteAllItems()
        componentList = self.__object.components.get()
        componentList.sort()
        if componentList:
            self.SetText('...')
            if selectComponent is None or selectComponent not in componentList:
                selectComponent=componentList[0]
            for component in componentList:
                ref = weakref.ref(component)
                item = self.listCtrl.AddItem(component.__class__.__name__, 
                                         ref)
                if component == selectComponent:
                    retValue = item
                    self.listCtrl.SelectItem(item)
                    self.SetText(component.__class__.__name__)
        else:
            self.SetText('')
            self.listCtrl.SetSelection(-1)
        return retValue
        
    def component_added(self, component):
        """component_added(component)

Call when 'component' is added to the object being viewed. 
"""
        index = self.refresh_components( component)
        if index is not None:
            self.listCtrl.SelectItem(index)
            self.SetText(component.__class__.__name__)
            
    def component_removed(self):
        """component_removed()
        
Call this when the selected component is removed from the object being viewed.
"""
        self.refresh_components()
            
    def get_selected(self):
        ref = self.listCtrl.GetSelectedData()
        if ref:
            return ref()
        else:
            return None
    
    def get_text(self):
        return self.listCtrl.GetStringValue()
        
        
######################################################################

class ComponentTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self,parent, style=wx.TR_HIDE_ROOT
                                |wx.TR_HAS_BUTTONS
                                |wx.TR_SINGLE
                                |wx.TR_LINES_AT_ROOT
                                |wx.SIMPLE_BORDER)
        self.SetSpacing(10)
        self.SetIndent(8)            

    def AddItem(self, text, data=None, parent=None):
        if not parent:
            root = self.GetRootItem()
            if not root:
                root = self.AddRoot("<hidden root>")
            parent = root

        item = self.AppendItem(parent, text)
        if data:
            self.SetItemPyData(item,data)
        return item     
    
    def FindItemByData(self, data, parentItem=None):  
        if parentItem == None:
            parentItem = self.GetRootItem()
        item, cookie = self.GetFirstChild(parentItem)
        while item:
            if self.GetPyData(item) == data:
                return item
            if self.ItemHasChildren(item):
                item = self.FindItemByData(data, item)
                if item:
                    return item
            item, cookie = self.GetNextChild(parentItem, cookie)
        return None

    
    def GetComponentItemByPosition(self, position):
        item, flags = self.HitTest(position)
        if item and flags & wx.TREE_HITTEST_ONITEMLABEL \
                and self.GetChildrenCount(item) == 0:
            return item
        return None
        
    def CreateComponentTree(self, object=None):
        """CreateComponentTree(tree,object)
    
Fills a TreeCtrl with components.

tree: the tree to fill
object: the object that is being viewed. Used to define what components are
    appropriate. If None, the tree will be filled with ALL components.
"""
        # process the available components
        types = {}
        from pug.all_components.util import get_all_components
        componentList = get_all_components()
        if componentList:
            for idx in range(len(componentList)-1,-1,-1):
                component = componentList[idx]
                if not is_valid_component_class(object,component):
                    continue
                # We have the right kind of component, sort by type
                _type = component._type
                if not _type:
                    _type = component._set
                    if not _type:
                        _type = "~Miscellaneous~"
                _type.strip()
                if not types.has_key(_type):
                    types[_type]=[]
                # Add the component to the list of components of this type
                types[_type].append(component)
        # Component's sorted... Now alphabetize
        typeList = types.keys()[:]
        typeList.sort()
        # Recreate tree
        self.DeleteAllItems()
        lastType = [] # we use a list because we're going to split by '/'
        parent = None # start at root
        # go through types, creating sections of the tree
        for _type in typeList:
            # do some hierarchy magic based on the fact that we sorted the names
            currentType = _type.split('/')
            level = 0 # level of label to check
            while level < len(lastType) and level < len(currentType):
                if lastType[level] == currentType[level]:
                    level+=1
                else:
                    break
            backup = len(lastType) - level # move back up the tree
            for i in range(backup):
                parent = self.GetItemParent(parent)
            addBranches = len(currentType) - level # number of branches to add
            for branch in currentType[-addBranches:]:
                parent = self.AddItem(branch,parent=parent)
            # now that we have the branches created, add the list of components
            componentList = types[_type]
            for component in componentList:
                self.AddItem(component.__name__, parent=parent, 
                             data=component) 
            self.SortChildren(parent)    
            lastType = currentType       
             

#----------------------------------------------------------------------
# This class is a popup containing a TreeCtrl.  This time we'll use a
# has-a style (instead of is-a like above.) Only allows buttom level tree
# nodes to be selected

class ComponentTreePopup(wx.combo.ComboPopup):
    """Popup control containing a tree"""
    # overridden ComboPopup methods    
    def Init(self):
        self.value = None
        self.curitem = None
        self.tooltip = ""
  
    def Create(self, parent):
        self.tree = ComponentTreeCtrl(parent)
        self.tree.Bind(wx.EVT_MOTION, self.OnMotion)
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)        
        
    def GetControl(self):
        return self.tree

    def GetStringValue(self):
        if self.value is not None:
            return self.tree.GetItemText(self.value)
        return ""

    def GetSelectedData(self):
        if self.value is not None:
            return self.tree.GetItemPyData(self.value)
        return None

    def OnPopup(self):
        if self.value:
            self.tree.EnsureVisible(self.value)
            self.tree.SelectItem(self.value)


    def SetStringValue(self, value):
        # this assumes that item strings are unique...
        root = self.tree.GetRootItem()
        if not root:
            return
        found = self.FindItem(value, root)
        if found:
            self.value = found
            self.tree.SelectItem(found)
        
    def SortChildren(self, item):
        return self.tree.SortChildren(item)

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return wx.Size(minWidth, min(200, maxHeight))
                       
    # helpers
    
    def FindItem(self, text, parentItem=None):  
        if parentItem == None:
            parentItem = self.tree.GetRootItem()
        item, cookie = self.tree.GetFirstChild(parentItem)
        while item.IsOk():
            if self.tree.GetItemText(item) == text:
                return item
            if self.tree.ItemHasChildren(item):
                item = self.FindItem(text, item)
                if item:
                    return item
            item, cookie = self.tree.GetNextChild(parentItem, cookie)
        return None
    
    def FindItemByData(self, data, parentItem=None):  
        return self.tree.FindItemByData(data, parentItem)
    
    def GetItemParent(self, item):
        return self.tree.GetItemParent(item)

    def PrependItem(self, text, data=None, parent=None):
        if not parent:
            root = self.tree.GetRootItem()
            if not root:
                root = self.tree.AddRoot("<hidden root>")
            parent = root

        item = self.tree.PrependItem(parent, text)
        if data:
            self.tree.SetItemPyData(item,data)
        return item
    
    def AddItem(self, text, data=None, parent=None):
        self.tree.AddItem( text, data, parent)

    def DeleteAllItems(self):
        return self.tree.DeleteAllItems
    
    def OnMotion(self, evt):
        # have the selection follow the mouse, like in a real combobox
        item, flags = self.tree.HitTest(evt.GetPosition())
        if item and flags & wx.TREE_HITTEST_ONITEMLABEL:
            self.tree.SelectItem(item)
            self.curitem = item
            component = self.tree.GetItemPyData(item)
            if component is None:
                doc = ""
                self.tree.SetToolTipString("")
                self.tree.SetToolTip(None)
            else:
                doc = component.__doc__
                doc = doc.replace('\n', ' ')                    
                if self.tooltip != doc:
                    self.tree.SetToolTipString(doc)
                    self.tree.GetToolTip().SetDelay(0.5)
            self.tooltip = doc
        evt.Skip()
        
    def SelectItem(self, item):
        self.tree.SelectItem(item)
        self.curitem = item
        self.value = item

    def OnLeftDown(self, evt):
        # do the combobox selection
        item = self.tree.GetComponentItemByPosition(evt.GetPosition())
        if item:
            self.curitem = item
            self.value = item
            self.Dismiss()
        evt.Skip()
    