import os
from fnmatch import fnmatch

import wx

class FileTree(wx.TreeCtrl):
    """FileTree(self, parent, id=-1, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE, 
                 validator=wx.DefaultValidator, name="", 
                 rootfolder=None, file_filter=("*.*"))

rootfolder: the starting folder. Default to current working folder.
file_filter: a list of patterns to match filenames against. for example:
    ("*.py","*.pyw","python.*")

Note: this control ignores files that start with '.'.
"""
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE, 
                 validator=wx.DefaultValidator, name="", 
                 rootfolder=".", file_filter=("*.*")):
        wx.TreeCtrl.__init__( self, parent, id, pos, size, style, validator,
                              name)
        self.file_filter = file_filter
        il = wx.ImageList(16,16)
        self.fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER,
                                                       wx.ART_OTHER, (16,16))) 
        self.fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,
                                                          wx.ART_OTHER,(16,16)))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, 
                                                       wx.ART_OTHER,(16,16)))

        self.AssignImageList(il)
        try:
            rootfolder = os.path.realpath(rootfolder)
        except:
            raise ValueError, "file_tree invalid root folder:",rootfolder
        root = self.AddRoot(os.path.split(rootfolder)[1])
        self.SetItemImage(root,self.fldridx,wx.TreeItemIcon_Normal)
        self.SetItemImage(root, self.fldropenidx,wx.TreeItemIcon_Expanded)

        self.AddTreeNodes(root, rootfolder)
        try:
            self.Expand(root)
        except:
            # not if we have a hidden root
            pass
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpand)
    
    def Refresh(self, item=None):
        "Refresh the tree from the given item. If item is none, refresh all"
        if item is None:
            item = self.GetRootItem()
        self.DeleteChildren(item)
        self.AddTreeNodes(item)
        
    def OnExpand(self, event):
        self.Refresh( event.GetItem())

    def AddTreeNodes(self, parentItem, rootfolder=None):
        if rootfolder == None:
            rootfolder = self.GetPyData(parentItem)
        items = os.listdir(rootfolder)
        items = sorted(items,key=str.lower)
        folders = []
        files = []
        for item in items:
            if item[0]==".":
                continue
            itempath = os.path.join(rootfolder, item)
            if os.path.isfile(itempath):
                fileok=False
                for filter in self.file_filter:
                    if fnmatch(item, filter):
                        fileok=True
                        break
                if fileok:
                    files.append((item,itempath))
            else:
                folders.append((item,itempath))
        for folder, itempath in folders+files:
            newItem = self.AppendItem(parentItem, folder)
            if os.path.isfile(itempath):
                self.SetItemImage(newItem, self.fileidx,wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(newItem, self.fldridx,wx.TreeItemIcon_Normal)
                self.SetItemImage(newItem, self.fldropenidx,
                                  wx.TreeItemIcon_Expanded)    
                self.AddTreeNodes(newItem, itempath)
            self.SetPyData( newItem, itempath)
            
    def GetFilePath(self):
        return self.GetPyData(self.GetSelection())
