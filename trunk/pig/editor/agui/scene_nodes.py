"""Scene Nodes attribute gui... a tree window (also defined here)"""
import weakref
from functools import partial

from pig.PigDirector import PigDirector

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
        control = wx.Panel(window)
        sizer = wx.BoxSizer()
        control.SetSizer(sizer)
        self.list = NodeTreeListCtrl(window.object, parent=control)
        control.SetMinSize( (self.list.get_full_width()+10, -1))
        sizer.Add( self.list, 1, wx.EXPAND)
        #control.SetMinSize((control.get_full_width(), -1))
        kwargs['control_widget'] = control
        Base.__init__(self, attribute, window, aguidata, **kwargs)
        
    def refresh(self, event=None):
        if PigDirector.project_started:
            self.list.refresh_tree()
        Base.refresh(self, event)
        
    def setup(self, attribute, window, aguidata={}):
        aguidata.setdefault('control_only',True)
        self.list.set_object( window.object)
        Base.setup( self, attribute, window, aguidata)
        
    def tree_view(self, event=None):
        app = wx.GetApp()        
        if wx.GetKeyState(wx.WXK_CONTROL) or \
                    not app.show_object_frame(self.window.object.nodes):
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
        app.frame_started_viewing( self, scene.nodes)           
            
class NodeTreeListCtrl( TreeListCtrl):
    """NodeTreeListCtrl( TreeListCtrl)
    
A tree control that shows all the nodes in an Opioid2D scene.
"""
    changing_sel = False
    object = None
    auto_refresh = True
    def __init__(self, scene, *args, **kwargs):
        """__init__(scene, *args, **kwargs) 
        
Special kwargs:
    style: style applied to the wx.gizmos.TreeListCtrl. Default is 
                      wx.TR_HIDE_ROOT \
                    | wx.TR_DEFAULT_STYLE \
                    | wx.TR_HAS_BUTTONS  \
                    | wx.TR_FULL_ROW_HIGHLIGHT \
                    | wx.TR_SINGLE \
                    | wx.TR_NO_LINES
"""
        style = kwargs.pop('style',-1)
        if style is -1:
            style = wx.TR_HIDE_ROOT \
                    | wx.TR_DEFAULT_STYLE \
                    | wx.TR_HAS_BUTTONS  \
                    | wx.TR_FULL_ROW_HIGHLIGHT \
                    | wx.TR_SINGLE \
                    | wx.TR_NO_LINES
            # can't figure out how to make the list single selection
            # hacked below
        TreeListCtrl.__init__(self, style=style, *args, **kwargs)
        # columns
        self.Indent = 0 # doesn't seem to work
        self.AddColumn("gname")
        self.AddColumn("class")
        self.AddColumn("layer")
        self.SetColumnWidth(0,80)
        self.set_object(scene)
        self.refresh_tree()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activated)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)
        self.menu_up = wx.NewId()
        self.menu_down = wx.NewId()
        self.menu_top = wx.NewId()
        self.menu_bottom = wx.NewId()
        self.Bind(wx.EVT_MENU, self.move_up, id=self.menu_up)
        self.Bind(wx.EVT_MENU, self.move_down, id=self.menu_down)
        self.Bind(wx.EVT_MENU, self.move_top, id=self.menu_top)
        self.Bind(wx.EVT_MENU, self.move_bottom, id=self.menu_bottom)
        self.right_clicked = None
        wx.GetApp().register_selection_watcher(self)
        from pug.syswx.pugframe import PugFrame
        self.PugFrame = PugFrame
        
    def on_right_click(self, event):
        menu = wx.Menu()
        menu.Append(self.menu_up,"Move up in layer")
        menu.Append(self.menu_down,"Move down in layer")
        menu.Append(self.menu_top,"Move to top of layer")
        menu.Append(self.menu_bottom,"Move to bottom of layer")
        self.right_clicked = self.GetPyData(event.Item)()
        self.PopupMenu(menu)
        menu.Destroy()
        
    def move_up(self, event=None):
        self.arrange( 1)
        
    def move_down(self, event=None):
        self.arrange( -1)
        
    def move_top(self, event=None):
        c_nodes = self.right_clicked.layer._layer.GetNodes()
        idx = self.right_clicked.layer.get_node_idx(self.right_clicked)
        self.arrange( len(c_nodes) - idx - 1)
                 
    def move_bottom(self, event=None):
        idx = self.right_clicked.layer.get_node_idx(self.right_clicked)
        self.arrange( -idx)
        
    def arrange(self, delta):
        layer = self.right_clicked.layer
        do_fn = partial(self.do_arrange, layer, self.right_clicked, delta)
        undo_fn = partial(self.do_arrange, layer, self.right_clicked, -delta)
        do_fn()
        wx.GetApp().history.add("Arrange node", undo_fn, do_fn)
        self.right_clicked = None
        
    def do_arrange( self, layer, node, delta):
        layer.move_node( node, delta)
        self.object.nodes.doCallbacks() # let guis know nodes changed
        self.SelectItem( self.find_item_by_data(weakref.ref(node)))

    def set_object(self, scene):
        try:
            if self.object and self.object.nodes:
                self.object.nodes.unregister(self.nodes_changed)
        except:
            #object is probably destroyed already
            pass
        self.object = scene
        self.object.nodes.register(self.nodes_changed)
        self.refresh_tree()
        
    def on_set_selection(self, selectedObjectDict=None):
        """Callback from pug App"""
        if self.changing_sel:
            return
        self.changing_sel = True
        if selectedObjectDict == None:
            selectedObjectDict = wx.GetApp().selectedObjectDict
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
        try:
            item, cookie = self.GetFirstChild(parentItem)
        except:
            return None
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
                app = wx.GetApp()
                app.set_selection([node])
                self.changing_sel = False
        
    def on_activated(self, event):
        item = event.Item
        if item:
            node = self.GetPyData(item)
            if node:
                node = node()
            if node:
                app = wx.GetApp()
                if not app.show_object_frame(node) or \
                        wx.GetKeyState(wx.WXK_CONTROL):
                    self.PugFrame(node)
 
    def nodes_changed(self, nodes=None, func=None, arg1=None, arg2=None):
        # TODO: make this more efficient by making more specific changes
        try:
            if PigDirector.project_started and not PigDirector.paused:
                return
        except:
            pass
        if not self.auto_refresh:
            return
        if not self.refreshing:
            wx.CallAfter(self.refresh_tree)
        self.refreshing = True
        
    def refresh_tree(self):
        try:
            nodes = self.object.get_ordered_nodes()
        except:
            #object is probably destroyed
            self.DeleteAllItems()
            return
        self.Freeze()
        self.DeleteAllItems()
        self.root = self.AddRoot("Invisible Root") # this won't be shown        
#        self.DeleteChildren(self.root)
        self.SetMainColumn(1)
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
        self.on_set_selection()
        self.refreshing = False
        if self.IsFrozen():
            self.Thaw()
        
    def get_full_width(self):
        w = 0
        for column in range(self.GetColumnCount()):
            w += self.GetColumnWidth(column) 
        return w
        