"""Scene Nodes attribute gui... a tree window (also defined here)"""
import weakref

import wx
from wx.gizmos import TreeListCtrl

from pug.syswx.attributeguis import Base
from pug.syswx.wxconstants import WX_SCROLLBAR_FUDGE

class SceneNodes (Base):
    """An attribute gui that's a tree window for working with Scene nodes

SceneNodes(attribute, window, aguidata, **kwargs)
aguidata: possible entries-
    'auto_open': automatically open the tree view when gui is created. 
                Default is False
attribute: what attribute of window.object is being controlled
window: the parent window. 
For other kwargs arguments, see the Base attribute GUI
"""
    refreshing = False
    def __init__(self, attribute, window, aguidata={}, **kwargs):
        self.tree = None
        # control
        control = NodeTreeListCtrl(window.object, parent=window)
        #control.SetMinSize((control.get_full_width(), -1))
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def setup(self, attribute, window, aguidata={}):
        aguidata.setdefault('control_only',True)
        self.control.set_object( window.object)
        self.control.SetMinSize( (self.control.get_full_width() + 5, -1))
        Base.setup( self, attribute, window, aguidata)
        
    def tree_view(self, event=None):
        app = wx.GetApp()        
        if wx.GetKeyState(wx.WXK_CONTROL) or \
                    not app.show_object_pugframe(self.window.object.nodes):
            name = self.window.shortPath
            if not name:
                name = self.window.Title
            title = ' '.join([name,'Node-Tree'])
            self.tree = NodeTreeFrame( self.window.object, 
                                       parent=self.window, 
                                  title=title)
            self.tree.Show()
        
class NodeTreeFrame( wx.Frame):
    def __init__(self, scene, parent=None, title=None, *args, **kwargs):
        if title is None:
            title = ''.join([scene.__class__.__name__, ' Node-Tree'])
        wx.Frame.__init__(self, parent, title=title, *args, **kwargs)
        #self.SetMinSize((100,100))
        self.CreateStatusBar()
        sizer = wx.BoxSizer()
        self.SetSizer(sizer)
        self.tree = NodeTreeListCtrl( scene, parent=self)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetClientSize((self.tree.get_full_width(), self.Size[1]))
        app = wx.GetApp()
        app.pugframe_viewing( self, scene.nodes)           
            
class NodeTreeListCtrl( TreeListCtrl):
    """NodeTreeListCtrl( TreeListCtrl)
    
A tree control that shows all the nodes in an Opioid2D scene.
"""
    changing_sel = False
    object = None
    def __init__(self, scene, *args, **kwargs):
        """__init__(scene, *args, **kwargs) 
        
Special kwargs:
    style: style applied to the wx.gizmos.TreeListCtrl. Default is 
                      wx.TR_HIDE_ROOT \
                    | wx.TR_DEFAULT_STYLE \
                    | wx.TR_HAS_BUTTONS  \
                    | wx.TR_FULL_ROW_HIGHLIGHT \
                    | wx.TR_ROW_LINES
"""
        style = kwargs.pop('style',-1)
        if style is -1:
            style = wx.TR_HIDE_ROOT \
                    | wx.TR_DEFAULT_STYLE \
                    | wx.TR_HAS_BUTTONS  \
                    | wx.TR_FULL_ROW_HIGHLIGHT \
                    | wx.TR_SINGLE 
            # can't figure out how to make the list single selection
            # hacked below
        TreeListCtrl.__init__(self, style=style, *args, **kwargs)
        # columns
        self.Indent = 5 # doesn't seem to work
        self.AddColumn("gname")
        self.AddColumn("class")
        self.AddColumn("layer")
        self.SetColumnWidth(0,80)
        self.set_object(scene)
        self.refresh_tree()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
#        self.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.dclick)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activated)
        wx.GetApp().register_selection_watcher(self)
        from pug.syswx.pugframe import PugFrame
        self.PugFrame = PugFrame
        
    def set_object(self, scene):
        if self.object and self.object.nodes:
            self.object.nodes.unregister(self.nodes_changed)
        self.object = scene
        self.object.nodes.register(self.nodes_changed)
        self.refresh_tree()
        
    def on_set_selection(self, selectedObjectDict):
        """Callback from pug App"""
        self.changing_sel = True
        self.UnselectAll()
        if selectedObjectDict:
            count = 0
            for ref in selectedObjectDict.itervalues():
                item = self.find_item_by_data( ref)
                if item:
                    self.SelectItem(item)
                    if count == 0:
                        self.EnsureVisible(item)
                    count += 1
        self.changing_sel = False
        
    def find_item_by_data(self, data, parentItem=None):  
        if parentItem == None:
            parentItem = self.GetRootItem()
        item, cookie = self.GetFirstChild(parentItem)
        while item:
            if self.GetPyData(item) == data:
                return item
            if self.ItemHasChildren(item):
                item = self.find_item_by_data(data, item)
                if item:
                    return item
            item, cookie = self.GetNextChild(parentItem, cookie)
        return None
    
    def on_sel_changed(self, event):
        if self.changing_sel:
            # let's avoid infinite recursion, shall we?
            return
        item = event.Item
        if item:
            node = self.GetPyData(item)
            if node:
                node = node()
            if node:
                self.changing_sel = True
                self.UnselectAll()
                self.SelectItem(item)
                self.changing_sel = False
                app = wx.GetApp()
                app.set_selection([node])
        
    def on_activated(self, event):
        item = event.Item
        if item:
            node = self.GetPyData(item)
            if node:
                node = node()
            if node:
                app = wx.GetApp()
                if not app.show_object_pugframe(node) or \
                        wx.GetKeyState(wx.WXK_CONTROL):
                    self.PugFrame(node)
 
    def nodes_changed(self, nodes, func, arg1, arg2):
        # TODO: make this more efficient by making more specific changes
        if not self.refreshing:
            wx.CallAfter(self.refresh_tree)
        self.refreshing = True
        
    def refresh_tree(self):
        self.Freeze()
        nodes = self.object.nodes
        self.DeleteAllItems()
        self.root = self.AddRoot("Invisible Root") # this won't be shown        
#        self.DeleteChildren(self.root)
        self.SetMainColumn(1)
        nodes = self.object.get_ordered_nodes()
        for node in nodes:
            cls = node.__class__.__name__
            if node.archetype:
                cls = ''.join(['* ',cls])
            gname = getattr(node, 'gname', '')
            if not gname:
                gname = ''
            layer = str(node.layer_name)
            item = self.AppendItem(self.root, cls)
            self.SetPyData(item, weakref.ref(node))
            self.SetItemText(item, gname, 0)
            self.SetItemText(item, layer, 2)
        self.SetMainColumn(2)
        self.refreshing = False
        if self.IsFrozen():
            self.Thaw()
        
    def get_full_width(self):
        w = 0
        for column in range(self.GetColumnCount()):
            w += self.GetColumnWidth(column) 
        return w
        