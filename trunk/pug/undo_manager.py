import wx

class UndoManager():
    def __init__(self):
        self.list = []
        self.index = 0
        self.last_id = None
        
    def add(self, description, undo_fn, do_fn, id=None):
        """add(item, id=None)
    
Add an undo item to the undo list.
description: a simple, human readable description
unfo_fn: a callable that undoes the action
do_fn: a callable that redoes the action    
id: an optional id for grouping undo items. All consecutive undo items with the
    same id will be undone and redone as a group. A value of None always starts
    a new group
"""
        self.list = self.list[:self.index]
        if id is None or id != self.last_id:
            self.list.append("MARK")
            self.index += 1
        self.list.append({"description":description,
                          "undo_fn":undo_fn,
                          "do_fn":do_fn})
        self.index += 1
        print self.list, self.index
        
    def undo(self):
        "undo(): undo the most recent undo item or undo item group"
        while self.list[self.index-1] != "MARK":  
            cmd_dict = self.list[self.index-1]
            cmd_dict["undo_fn"]()
            self.index -= 1
        self.index -= 1 # past mark
        wx.GetApp().refresh()
        print self.list, self.index
        
    def redo(self):
        "redo(): redo the most recent undone item or item group"
        if self.index < len(self.list) - 1:
            self.index += 1 # skip mark
            while self.index < len(self.list)-1 and self.index != "MARK":
                cmd_dict = self.list[self.index]
                cmd_dict["do_fn"]()
                self.index += 1
        wx.GetApp().refresh()
                